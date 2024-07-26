"""
Utilities for loading and converting the CSV files from the USDA into
data that cronometer can read.

Most of the stuff in this file are helpers which can be used separately if
needed, but a majority of the functionality is rolled up in the
convertUsdaFoods function which will convert one type of USDA data.

Usage is something like:

from cronometer.foods import nutritionInfo
from cronometer.datasource import usdaFoodLoader

foodDir = # Full Path to the download CSV files
nutInfo = nutritionInfo.loadNutrientInfo()
usdaFoodLoader.convertUsdaFoods(foodDir, nutInfo, FoodSource.SURVEY)
"""
import contextlib
import csv
import difflib
import os
import zipfile

from collections import defaultdict
from collections import namedtuple
from datetime import date
from itertools import groupby
from pathlib import Path
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict

import cronometer.util.toolbox as toolbox

from cronometer.foods.food import Food
from cronometer.foods.food import FoodNutrient
from cronometer.foods.food import FoodSource
from cronometer.foods.measure import GRAM
from cronometer.foods.measure import Measure
from cronometer.foods.nutritionInfo import LegacyNutrientInfos
from cronometer.foods.nutritionInfo import NutrientInfo
from cronometer.foods.nutritionInfo import NutrientInfos
from cronometer.foods.nutritionInfo import NutrientUnit

THIS_DIR = Path(os.path.dirname(__file__))


SR_LEGACY_FOODS_CSV = "sr_legacy_food.csv"
FOOD_CSV = "food.csv"
NUTRIENT_CSV = "nutrient.csv"
MEASURE_CSV = "measure_unit.csv"
PORTION_CSV = "food_portion.csv"
FOOD_NUTRIENT_CSV = "food_nutrient.csv"
CONVERSION_CSV = "food_calorie_conversion_factor.csv"
FOOD_CONVERSION_CSV = "food_nutrient_conversion_factor.csv"
BRANDED_CSV = "branded_food.csv"


@contextlib.contextmanager
def _openCSV(csvFile: Union[Path, str]):
    """
    Open a CSV file and yield back an iterator over the rows with the
    first row (the header) removed.
    """
    with open(csvFile) as f:
        reader = csv.reader(f)
        next(reader) # remove the headers
        yield reader


class CsvFood(BaseModel):
    """
    A food entry read from the food.csv file.
    """
    model_config = ConfigDict(frozen=True)

    foodSource: FoodSource
    fid: int
    legacyId: Optional[int] = None
    name: str


class CsvNutrient(BaseModel):
    """
    A nutrient entry read from the nutrients.csv file.
    """
    model_config = ConfigDict(frozen=True)

    nid: int
    """ The Id used in the USDA csv data """
    name: str
    """ The name of the nutrient """
    legacyId: Optional[float]
    """ The id value used in the java version of cronometer. """
    unit: NutrientUnit
    """ The unit of measure used in the USDA csv data. """


class CsvMeasure(BaseModel):
    """
    A portion's measurement name read from the measure_unit.csv file
    """
    model_config = ConfigDict(frozen=True)

    pid: int
    name: str


class CsvPortion(BaseModel):
    """
    A Portion entry read from the food_portion.csv file.
    """
    model_config = ConfigDict(frozen=True)

    fid: int
    """ The id of the food this portion is for """
    seqNum: int
    """ An ordering value for how to list the portion """
    amount: float
    """ The numeric part of the portion. Not set for foundation foods."""
    measureId: int
    """ The id matching the CsvMeasure data. if this is 9999, it is legacy and
        won't have a matching CsvMeasure value"""
    description: str
    """ The foundation foods description of what the portion is """
    modifier: str
    """ Description of portion for non-foundation food. Qualifier for
        foundation foods"""
    grams: float


class CsvFoodNutrient(namedtuple("CsvFoodNutrient", ["fid", "nid", "amount"])):
    """
    A single nutrient value for a food read from the food_nutrient.csv
    file.

    This data is all nutrient per 100g of the food.

    This is using a namedtuple vs pydantic because the initialization speed
    penalty from pedantic is substantial when reading 26 million nutrient
    records from a file.

    fid: int
      The id of the food this nutrient is for
    nid: int
      The id of the nutrient
    amount: float
      The nutrient amount per 100g of the food
    """
    __slots__ = ()


class CsvConversion(BaseModel):
    """
    The calorie conversion values read from the
    food_calorie_conversion_factor.csv file.
    """
    cid: int
    protein: Optional[float]
    fat: Optional[float]
    carb: Optional[float]


class CsvBrandedFood(BaseModel):
    """
    The branded food extra information read from the branded_food.csv
    file
    """
    fid: int
    owner: str
    brand: str
    subbrand: str
    measure: Optional[Measure]
    discontinued: Optional[date]


def loadLegacyIds(csvDir: Union[str, Path]) -> dict[int, int]:
    """
    Load the mapping of new USDA to the old legacy ids from the
    sr_legacy_food.csv file.

    The java version of cronometer used the legacy ids to identify
    foods, so that value is needed when reading/converting legacy
    files.
    """
    toRet = dict[int, int]()
    csvFile = os.path.join(csvDir, SR_LEGACY_FOODS_CSV)
    with _openCSV(csvFile) as reader:
        for row in reader:
            newId = int(row[0])
            oldId = int(row[1])
            toRet[newId] = oldId
    return toRet


def loadNutrients(csvDir: Union[str, Path]) -> list[CsvNutrient]:
    """
    Load all the nutrients found in the nutrients.xml csv file.
    """
    toRet = list[CsvNutrient]()
    csvFile = os.path.join(csvDir, NUTRIENT_CSV)
    with _openCSV(csvFile) as reader:
        for row in reader:
            nid = int(row[0])
            name = row[1]
            legacyId = float(row[3]) if row[3] else None
            unitStr = row[2].lower()
            if unitStr == "ug":
                unitStr = "µg"
            unit = NutrientUnit(unitStr)
            nut = CsvNutrient(nid=nid, name=name, legacyId=legacyId, unit=unit)
            toRet.append(nut)
    return toRet


def generateNutrientInfo(csvData: list[CsvNutrient],
                         legacyData: LegacyNutrientInfos) -> NutrientInfos:
    """
    Combine the data from the USDA csv files and the cronometer legacy
    nutrients.xml to create a final nutrient data set.
    """
    nutList = list()
    legacyIdToUsda = {n.legacyId : n for n in csvData}
    for lni in legacyData.nutrients:
        usdaIds = list()
        for legId in lni.usda:
            usdaNi = legacyIdToUsda[legId.index]
            if usdaNi.unit != lni.unit:
                raise ValueError(f"Cannot match unit type of {lni} to USDA"
                                 f" nutrient {usdaNi}")
            usdaIds.append(usdaNi.nid)
        ni = NutrientInfo(name=lni.name,
                          unit=lni.unit,
                          category=lni.category,
                          rdi=lni.rdi,
                          parentName=lni.parentName,
                          legacyIds=[i.index for i in lni.usda],
                          usdaIds=usdaIds,
                          sparse=lni.sparse,
                          track=lni.track,
                          dris=lni.dris,
                          cronIndex=lni.index)
        nutList.append(ni)
    return NutrientInfos(nutrients=nutList)


def loadCalorieConversion(csvDir: Union[str, Path]) -> list[CsvConversion]:
    """
    Load all the calorie conversions found in food_calorie_conversion_factor.csv
    """
    toRet = list[CsvConversion]()
    csvFile = os.path.join(csvDir, CONVERSION_CSV)
    with _openCSV(csvFile) as reader:
        for row in reader:
            cid = int(row[0])
            protein = float(row[1]) if row[1] else None
            fat = float(row[2]) if row[2] else None
            carb = float(row[3]) if row[3] else None
            conv = CsvConversion(cid=cid, protein=protein, fat=fat, carb=carb)
            toRet.append(conv)
    return toRet


def loadFoodConversions(csvDir: Union[str, Path]) -> dict[int, int]:
    """
    Load all the mappings of food ids to conversion ids from the
    food_nutrient_conversion_factor.csv file.

    The return value is a dict where the key is the food id and the
    value in the conversion id (the id in the CsvConversion object).
    """
    toRet = dict[int, int]()
    csvFile = os.path.join(csvDir, FOOD_CONVERSION_CSV)
    with _openCSV(csvFile) as reader:
        for row in reader:
            cid = int(row[0])
            fid = int(row[1])
            toRet[fid] = cid
    return toRet


def generateFoodConversion(csvDir: Union[str, Path]) -> dict[int, CsvConversion]:
    """
    Generate a mapping of food id to the calorie conversion values that
    should be used for the food.

    This will be a sparse dictionary because most foods do not seem to
    have this value
    """
    toRet = dict[int, CsvConversion]()
    calConversions = loadCalorieConversion(csvDir)
    foodConversions = loadFoodConversions(csvDir)

    calConvMap = {e.cid : e for e in calConversions}
    for fid, cid in foodConversions.items():
        calConv = calConvMap.get(cid)
        if calConv:
            toRet[fid] = calConv

    return toRet


def loadFoods(csvDir: Union[str, Path],
              legacyIdMap: dict[int, int]) -> list[CsvFood]:
    """
    Load all the foods found in the food.csv file (the main list of
    all the foods).

    The legacyIdMap is used to correlate the new USDA id for foods with
    the old legacy ID that the Java version of crononmeter used.
    """
    toRet = list[CsvFood]()
    csvFile = os.path.join(csvDir, FOOD_CSV)
    with _openCSV(csvFile) as reader:
        for row in reader:
            fid = int(row[0])
            fsrc = FoodSource(row[1])
            name = row[2]
            legacyId = None if fsrc != FoodSource.LEGACY else legacyIdMap[fid]
            food = CsvFood(foodSource=fsrc,
                           fid=fid,
                           name=name,
                           legacyId=legacyId)
            toRet.append(food)
    return toRet


def loadMeasures(csvDir: Union[str, Path]) -> list[CsvMeasure]:
    """
    Load all the measurement names from the measure_unit.csv file.
    """
    toRet = list[CsvMeasure]()
    csvFile = os.path.join(csvDir, MEASURE_CSV)
    with _openCSV(csvFile) as reader:
        for row in reader:
            pid = int(row[0])
            name = row[1]
            measure = CsvMeasure(pid=pid, name=name)
            toRet.append(measure)
    return toRet


def loadPortions(csvDir: Union[str, Path]) -> list[CsvPortion]:
    """
    Load all the portions from the food_portion.csv file.
    """
    toRet = list[CsvPortion]()
    csvFile = os.path.join(csvDir, PORTION_CSV)
    with _openCSV(csvFile) as reader:
        for row in reader:
            fid = int(row[1])
            seqNum = int(row[2]) if row[2] else 1
            amount = float(row[3]) if row[3] else 0.0
            measureId = int(row[4])
            desc = row[5]
            modifier = row[6]
            grams = float(row[7])
            portion = CsvPortion(fid=fid,
                                 seqNum=seqNum,
                                 amount=amount,
                                 measureId=measureId,
                                 description=desc,
                                 modifier=modifier,
                                 grams=grams)
            toRet.append(portion)
    return toRet


def generateMeasures(portions: list[CsvPortion],
                     measures: list[CsvMeasure]) -> dict[int, list[Measure]]:
    """
    Generate the cronometer measures from the csvData.

    Returns a dict that is keyed with the food index with the values being the
    list of measures for that food.
    """
    toRet = dict[int, list[Measure]]()

    measureDict = {m.pid : m.name for m in measures}

    for fid, pors in groupby(sorted(portions, key=lambda x: x.fid),
                             key=lambda x: x.fid) :
        measureList = list[Measure]()
        for por in pors:
            descList = list()
            if por.measureId != 9999:
                descList.append(measureDict[por.measureId])
            if por.description:
                descList.append(por.description)
            if por.modifier:
                descList.append(por.modifier)
            measure = Measure(grams=por.grams,
                              amount=por.amount,
                              description=" ".join(descList))
            measureList.append(measure)
        toRet[fid] = measureList

    return toRet


def loadFoodNutrients(csvDir: Union[str, Path],
                      filterIds: Optional[set[int]]=None,
                      nutrientIds: Optional[set[int]]=None) -> list[CsvFoodNutrient]:
    """
    Load all the food nutrient values from the food_nutrient.csv file.

    Takes two optional filters one of which is a list of ids for the foods whose
    nutrients are wanted and the other is the list of ids for the nutrients
    wanted. This is because the CSV file is 26 million lines or so and it
    is preferable to not load what isn't needed.
    """
    toRet = list[CsvFoodNutrient]()
    csvFile = os.path.join(csvDir, FOOD_NUTRIENT_CSV)
    with _openCSV(csvFile) as reader:
        for row in reader:
            fid = int(row[1])
            if filterIds is not None and fid not in filterIds:
                continue

            nid = int(row[2])
            if nutrientIds is not None and nid not in nutrientIds:
                continue

            amount = float(row[3])
            fn = CsvFoodNutrient(fid=fid, nid=nid, amount=amount)
            toRet.append(fn)
    return toRet


def loadOneFoodNutrients(csvDir: Union[str, Path],
                         tgtFid: int) -> list[CsvFoodNutrient]:
    """
    Load all the food nutrient values from the food_nutrient.csv file
    but only return ones that match the given fid.
    """
    toRet = list[CsvFoodNutrient]()
    csvFile = os.path.join(csvDir, FOOD_NUTRIENT_CSV)
    with _openCSV(csvFile) as reader:
        for row in reader:
            fid = int(row[1])
            if fid == tgtFid:
                nid = int(row[2])
                amount = float(row[3])
                fn = CsvFoodNutrient(fid=fid, nid=nid, amount=amount)
                toRet.append(fn)
    return toRet


def loadBrandedFoods(csvDir: Union[str, Path]) -> list[CsvBrandedFood]:
    """
    Loaded all the extra info for branded foods from the branded_food.csv
    file.
    """
    toRet = list[CsvBrandedFood]()
    csvFile = os.path.join(csvDir, BRANDED_CSV)

    with _openCSV(csvFile) as reader:
        for row in reader:
            fid = int(row[0])
            owner = row[1]
            brand = row[2]
            subbrand = row[3].capitalize()

            measure = None
            value = row[7]
            unit = row[8].lower()
            desc = row[9] or "labeled serving"
            if value:
                # Why does mg mean grams? who the f knows.
                # According to the USDA docs, this field is either
                # milliliters or grams. And that seems to be true even
                # though the values are whack. mc seems to be used for
                # grams in some cases but also ml. But I think all the
                # ml cases are basically water, where g = ml, so for now
                # we're just going to treat them the same.
                if unit in ("g", "grm", "mg", "gm", "iu", "mc", ""):
                    measure = Measure(grams=float(value),
                                      amount=0.0,
                                      description=desc)


            discontinued = row[16]
            if discontinued:
                discontinued = date.fromisoformat(discontinued)
            else:
                discontinued = None

            branded = CsvBrandedFood(fid=fid,
                                     owner=owner,
                                     brand=brand,
                                     subbrand=subbrand,
                                     measure=measure,
                                     discontinued=discontinued)
            toRet.append(branded)
        return toRet


def generateFoods(csvFoods: list[CsvFood],
                  measures: dict[int, list[Measure]],
                  conversion: dict[int, CsvConversion],
                  nutrientInfos: NutrientInfos,
                  nutrients: list[CsvFoodNutrient],
                  brandInfo: list[CsvBrandedFood]) -> list[Food]:
    """
    Construct the final cronometer Food objects from the information
    loaded from the USDA CSV Files.
    """
    toRet = list[Food]()

    brandDict = {b.fid : b for b in brandInfo}
    foodNutDict = defaultdict(list)
    for n in nutrients:
        foodNutDict[n.fid].append(n)

    for csvFood in csvFoods:
        foodNuts = foodNutDict[csvFood.fid]

        usdaIds = set()
        for f in foodNuts:
            usdaIds.add(f.nid)

        nutList = list[FoodNutrient]()
        for ni in nutrientInfos.nutrients:
            entries = [n for n in foodNuts if n.nid in ni.usdaIds]
            if entries:
                amount = sum((e.amount for e in entries))
                nutList.append(FoodNutrient(name=ni.name,
                                            amount=amount))

        bi = brandDict.get(csvFood.fid)
        name = csvFood.name

        m = measures.get(csvFood.fid) or list()

        if bi and bi.measure:
            m.append(bi.measure)

        if GRAM not in m:
            m.insert(0, GRAM)
        c = conversion.get(csvFood.fid)

        name = csvFood.name
        if bi:
            nameList = [name]
            if bi.owner and bi.brand:
                ratio = difflib.SequenceMatcher(None,
                                                bi.owner.lower(),
                                                bi.brand.lower()).ratio()
                if ratio < .5:
                    nameList.extend([bi.owner, bi.brand])
                else:
                    nameList.append(bi.brand)
            elif bi.owner:
                nameList.append(bi.owner)
            elif bi.brand:
                nameList.append(bi.brand)
            if bi.subbrand:
                nameList.append(bi.subbrand)
            name = ",".join(nameList)

        food = Food(name=name,
                    measures=m,
                    nutrients=nutList,
                    foodSource=csvFood.foodSource,
                    uid=csvFood.fid,
                    legacyUID=csvFood.legacyId,
                    # If None, pydantic will use default value
                    pCF=c.protein if c else None,
                    lCF=c.fat if c else None,
                    cCF=c.carb if c else None,
                    comments=[])
        if _fixOmegaFats(food, foodNuts):
            food.nutrients.sort(key=lambda x: nutrientInfos.indexOfName(x.name))
        toRet.append(food)
    return toRet


def writeFoodsToZip(foods: list[Food], zipPath: Union[str, Path]):
    """
    Write the given foods into a zip file
    """
    with zipfile.ZipFile(zipPath,
                         "w",
                         compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9) as archive:
        for food in foods:
            fileName = f"{food.uid}.json"
            with archive.open(fileName, "w") as f:
                f.write(food.model_dump_json(indent=2).encode())


def convertUsdaFoods(csvDir: Union[str, Path],
                     nutrientInfos: NutrientInfos,
                     foodSource: FoodSource,
                     cutDate: Optional[date]=None):
    """
    Load the CSV data for the USDA foods and generate a zip file
    containing json files for all the foods and an index file that can
    be used to understand what foods are available.

    These files will be generated into the user's cronometer config
    area.

    Cutdate is an optional value that will be used with Branded foods. If
    a branded food has a discontinued date that is before cutDate it will not
    be included in the final output.
    """
    userDir = toolbox.getUserDataDir()
    os.makedirs(userDir, exist_ok=True)

    csvmeasures = loadMeasures(csvDir)
    portions = loadPortions(csvDir)

    measures = generateMeasures(portions, csvmeasures)
    conversions = generateFoodConversion(csvDir)

    legacyIds = loadLegacyIds(csvDir)
    csvFoods = loadFoods(csvDir, legacyIds)

    sliced = sorted((f for f in csvFoods if f.foodSource == foodSource),
                    key=lambda x: x.fid)
    foodFilter = {f.fid for f in sliced}
    nutFilter = {n for ni in nutrientInfos.nutrients for n in ni.usdaIds}
    nutrients = loadFoodNutrients(csvDir, foodFilter, nutFilter)

    if foodSource == FoodSource.BRANDED:
        brandInfo = loadBrandedFoods(csvDir)
    else:
        brandInfo = list()

    if cutDate:
        foodsToCut = [bi.fid for bi in brandInfo if bi.discontinued and bi.discontinued < cutDate]
        if foodsToCut:
            sliced = [f for f in sliced if f.fid not in foodsToCut]

    newFoods = generateFoods(sliced,
                             measures,
                             conversions,
                             nutrientInfos,
                             nutrients,
                             brandInfo)
    zipPath = os.path.join(userDir, f"{foodSource.value}.zip")
    writeFoodsToZip(newFoods, zipPath)
    indexPath = os.path.join(userDir, f"{foodSource.value}.index")
    with open(indexPath, "w") as f:
        for food in newFoods:
            legId = f"{food.legacyUID}|||" if food.legacyUID else ""
            f.write(f"{legId}{food.uid}|{food.name}\n")


def _fixOmegaFats(food: Food, foodNuts: list[CsvFoodNutrient]) -> bool:
    """
    This is the algorithem from the original java cronometer for fixing
    Omega-3 and Omega-6 fat values. Taking their word for it that it works

    foodNuts should be a list of the CSV nutrients for a single food as
    should nutList. nutList should be fully ordered as it will be when
    passed into the Food constructor.

    ID mappings for the legacy fields to the new nutrient fields

    619 : 1270  PUFA 18:3
    685 : 1321  PUFA 18:3 n-6 c,c,c
    851 : 1404  PUFA 18:3 n-3 c,c,c (ALA)
    618 : 1269  PUFA 18:2
    675 : 1316  PUFA 18:2 n-6 c,c
    """
    def extractValue(nid: int) -> Optional[float]:
        """
        Grab a value out of the foodNuts list
        """
        try:
            return next(fn.amount for fn in foodNuts if fn.nid == nid)
        except StopIteration:
            return None

    w3a = food.nutrientValueByName("Omega-3")
    w6a = food.nutrientValueByName("Omega-6")

    n1270 = extractValue(1270)
    n1321 = extractValue(1321)
    n1404 = extractValue(1404)
    n1269 = extractValue(1269)
    n1316 = extractValue(1316)

    changed = False
    # linolenic acid
    if n1270 is not None:
        # if no data for the n-3 linolenic acid, use the parent value
        if n1404 is None:
            w3a += n1270
            if n1321 is not None:
                # subtract the n-6 sub-value, if we have a value
                w3a -= n1321
            food.setNutrientByName("Omega-3", w3a)
            changed = True

    # linoleic acid
    if n1269 is not None:
        # if no data for the n-6 linoleic acid, use the parent value
        if n1316 is None:
            w6a += n1269
            # could subtract other non-n6 children here...
            food.setNutrientByName("Omega-6", w6a)
            changed = True
    return changed

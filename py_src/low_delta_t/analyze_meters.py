"""
@author: sjm34
"""

from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from python_lib.utils import fetch_trends, build_index, build_df


SHOW_PLOTS = True
RECENT_DAYS = 7
METER_NAMES = (
    "AliceCookHouse.CW.FP/TONS",
    "AppelCommons.10064.FleximF721/CW.Tons",
    "BaileyHall.CW.FP/TONS",
    "BakerLab.CW.FP/TONS",
    "BarbaraMcClintockHall.B0061.FleximF721/CW.Tons",
    "BardHall.CW.FP/TONS",
    "BarnesHall.CW.FP/TONS",
    "BartonHall.CW.FP/TONS",
    "BeebeHall.LowerMER.FleximF721/CW.Tons",
    "BigRedBarn.10001.FleximF721/CW.Tons",
    "BiotechnologyBuilding.CW.FP/TONS",
    "BoyceThompsonInstitute.CW.FP/TONS",
    "BradfieldHall.CW.FP/TONS",
    "BrucknerLab.CW.FP/TONS",
    "CaldwellHall.CW.FP/TONS",
    "CampusStore.CW.ES749/TONS",
    "CarlBeckerHouse.CW.FP/TONS",
    "CarpenterHall.CW.FP/TONS",
    "ClarkHall.CW.FP/TONS",
    "ClinicalProgramsCenter.CW.FP/TONS",
    "ComputingCommunicationsCenter.CW.FP/TONS",
    "ComstockHall.CW.FP/TONS",
    "CorsonMuddComplex.CW.FleximF721/TONS",
    "CourtHall.CW.FP/TONS",
    "DayHall.CW.FP/TONS",
    "DuffieldHall.CW.FP/TONS",
    "EastCampusResearchFacility.CW.FP/TONS",
    "EmersonHall.CW.FP/TONS",
    "FernowHall.CW.FP/TONS",
    "FloraRoseHouse.CW.FP/TONS",
    "Foundry.RandMER.FleximF721/CW.Tons",
    "FriedmanWrestlingCenter.CW.FP/TONS",
    "GannettHealthCenter.CW.FP/TONS",
    "GatesHall.CW.FP/TONS",
    "GoldwinSmithHall.CW.FP/TONS",
    "GrummanHall.CW.FP/TONS",
    "HansBetheHouse.CW.FP/TONS",
    "HollisterHall.CW.FP/TONS",
    "HughesHall.CW.FleximF721/TONS",
    "HughesHall.CW.FP/TONS",
    "HumanEcologyBuilding.CW.FP/TONS",
    "HumphreysServiceBuilding.CW.FP/TONS",
    "HuShihHall.B0061.FleximF721/CW.Tons",
    "IthacaHighSchool.CW.FP/TONS",
    "IvesHall.CW.FP/TONS",
    "JohnsonMuseumOfArt.CW.FP/TONS",
    "KimballHall.CW.FleximF721/TONS",
    "KlarmanHall.CW.FP/TONS",
    "KrochLibrary.CW.FP/TONS",
    "LargeAnimalResearchTeachingUnit.CW.FP/TONS",
    "LincolnHall.CW.FP/TONS",
    "LynahRink.CW.FP/TONS",
    "MalottHall.CW.FP/TONS",
    "MannLibrary.CW.FP/TONS",
    "MarthaVanRensselaerComplex.MAIN.CW.FP/TONS",
    "MarthaVanRensselaerWest.CW.FleximF704/TONS",
    "MilsteinHall.CW.FP/TONS",
    "MorrillHall.CW.FP/TONS",
    "MorrisonHall.CW.FP/TONS",
    "MyronTaylorHall.CW.FP/TONS",
    "NewmanLab.CW.FP/TONS",
    "NoyesCommunityRecreationCenter.CW.FP/TONS",
    "OlinChemistryResearchWing.CW.FP/TONS",
    "OlinHall.CW.FP/TONS",
    "OlinLibrary.CW.FP/TONS",
    "PhillipsHall.CW.FP/TONS",
    "PhysicalSciences.CW.FP/TONS",
    "PlantScience.CW.FP/TONS",
    "RandHall.CW.FP/TONS",
    "RhodesHall.7thfloor.NOC.CW.FP/TONS",
    "RhodesHall.CW.FP/TONS",
    "RhodesHall.Telecom.CW.FP/TONS",
    "RileyRobbHall.CW.FP/TONS",
    "RobertPurcellCommunityCenter.CW.FP/TONS",
    "RobertWHolleyCenter.CW.FP/TONS",
    "RockefellerHall.CW.FP/TONS",
    "RuthBaderGinsburgHall.B0069.FleximF721/CW.Tons",
    "SageHall.CW.FP/TONS",
    "SavageHall.CW.FP/TONS",
    "SchoellkopfHall.CW.FP/TONS",
    "SchurmanHall.CW.FP/TONS",
    "SchurmanNorth.CW.FP/TONS",
    "SchwartzCenterForPerformingArts.CW.FP/TONS",
    "SibleyHall.CW.FP/TONS",
    "SneeHall.CW.FP/TONS",
    "SpaceSciencesBuilding.CW.FP/TONS",
    "StatlerHall.CW.FP/TONS",
    "StatlerHotel.CW.FP/TONS",
    "StimsonHall.CW.FP/TONS",
    "StockingHall.CW.FP/TONS",
    "ToniMorrisonHall.Bsmt.FleximF721/CW.TONS",
    "ToniMorrisonHall.Coolers.CW.FleximF721/TONS",
    "UpsonHall.CW.FP/TONS",
    "UrisHall.CW.FP/TONS",
    "UrisLibrary.CW.FP/TONS",
    "VetDiagnosticLab.CW.FP/TONS",
    "VetMedicalCenter.CW.FP/TONS",
    "VetResearchTower.CW.FP/TONS",
    "WardLab.CW.FP/TONS",
    "WarrenHall.CW.FP/TONS",
    "WeillHall.AHU-2.CW.FP/TONS",
    "WeillHall.AHU-3.CW.FP/TONS",
    "WeillHall.AHU-5.CW.FP/TONS",
    "WeillHall.CW.FP/TONS",
    "WeillHall.PlantGrowth.CW.FP/TONS",
    "WhiteHall.CW.FP/TONS",
    "WillardStraightHall.CW.FP/TONS",
    "WilliamKeetonHouse.CW.FP/TONS",
    "WilsonLab.400U.FleximF721/CW.CoolingLoops.Tons",
    "WilsonLab.400U.FleximF721/CW.ExperimentalHall.Tons",
    "WilsonLab.CW.FleximF721/TONS",
    "WilsonLab.CW.FP/TONS",
    "WingHall.CW.FP/TONS",
)


def list_to_df(records, column_name):
    """converts dataset list to dataframe"""
    a = np.array(records[column_name])
    return pd.DataFrame.from_records(a, columns=("ts", column_name), index="ts")


if __name__ == "__main__":

    # init some variables
    now = datetime.now()
    year_ago = now - timedelta(365)
    start_time = now - timedelta(RECENT_DAYS)
    a_total = 0.0
    b_total = 0.0
    int_total = 0.0
    count = 0
    # loop through the meter names
    for meter_name in METER_NAMES:
        device_name = meter_name[:-4]
        # point names for OAT, FLOW, TONS, STEMP, RTEMP
        if meter_name.endswith("TONS"):
            stemp_name = f"{device_name}STEMP"
            rtemp_name = f"{device_name}RTEMP"
            flow_name = f"{device_name}FLOW"
        elif meter_name.endswith("Tons"):
            stemp_name = f"{device_name}STemp"
            rtemp_name = f"{device_name}RTemp"
            flow_name = f"{device_name}Flow"

        oat_name = "GameFarmRoadWeatherStation.TAVG_H_F"
        tons_name = meter_name

        names = (oat_name, flow_name, tons_name, stemp_name, rtemp_name)
        # fetch previous year's tons for the meter
        tons = build_index(fetch_trends(
            point=tons_name, start_time=year_ago, end_time=now, additional= ["aggH"]
        ))
        # fetch recent period STEMP, RTEMP, FLOW, TONS, OAT
        recent_points = (stemp_name, rtemp_name, flow_name, tons_name, oat_name)
        recent = fetch_trends(points=recent_points,start_time=start_time, end_time=now)

        # compute estimated design load from max(tons) over past year
        max_tons = max(tons[tons_name].values())
        model_df = build_df(recent)
        if any(x not in model_df for x in recent_points):
            print(f"Missing trends from {recent_points}")
            continue
        # partial load ratio for the recent period from all fetched data
        model_df["PLR"] = model_df[tons_name] / max_tons
        # partial temperature ratio
        model_df["PT"] = (model_df[oat_name] - model_df[stemp_name]) / 41
        model_df["DT"] = model_df[rtemp_name] - model_df[stemp_name]
        fig = plt.figure(figsize=(10,8))
        ax = fig.add_subplot(projection = "3d")
        # show the model as a surface on a 40 x 40 grid
        x_m = pd.DataFrame(
            np.mgrid[0.001:1.001:0.025, 0.001:1.001:0.025].reshape(2, -1).T
        )
        # standard model
        pred = (x_m[0] ** 0.173 * x_m[1] ** 0.067 * 15.603).to_numpy()
        X = x_m[0].to_numpy().reshape(-1, 40)
        Y = x_m[1].to_numpy().reshape(-1, 40)
        Z = pred.reshape(-1, 40)

        # show a sample of the actuals as a scatterplot
        vis_df = model_df
        vis_x = np.array(vis_df["PLR"])
        vis_y = np.array(vis_df["PT"])
        vis_z = np.array(vis_df["DT"])

        # compute the extents
        plt_vmin = min(np.min(vis_z), np.min(Z))
        plt_vmax = max(np.max(vis_z), np.max(Z))
        # plot the surface and the scatter
        surf = ax.plot_surface(
            X, Y, Z, vmin=plt_vmin, vmax=plt_vmax, cmap=cm.coolwarm, alpha=0.5
        )
        scat = ax.scatter(
            vis_x,
            vis_y,
            vis_z,
            label="Actual DeltaT",
            vmin=plt_vmin,
            vmax=plt_vmax,
            c=vis_z,
            cmap=cm.coolwarm,
            alpha=.8
        )
        ax.set_title(device_name + " DeltaT", loc="left")
        ax.set_xlabel("PLR")
        ax.set_ylabel("PT")
        ax.set_zlabel("DT")
        plt.show()


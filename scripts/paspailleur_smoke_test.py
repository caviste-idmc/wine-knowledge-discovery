import paspailleur as psp
import pandas as pd


def main() -> None:
    df = pd.DataFrame(
        {
            "Type": ["Red", "White", "Red", "Rose", "Red", "White"],
            "Country": ["FR", "ES", "FR", "IT", "US", "US"],
            "ABV": [14.0, 12.0, 13.5, 11.5, 15.0, 12.5],
            "Body": ["Full", "Light", "Full", "Light", "Full", "Medium"],
        },
        index=[f"w{i}" for i in range(6)],
    )

    TypePattern = psp.pattern_factory("CategorySetPattern", Universe=tuple(sorted(df["Type"].unique())))
    CountryPattern = psp.pattern_factory("CategorySetPattern", Universe=tuple(sorted(df["Country"].unique())))
    BodyPattern = psp.pattern_factory("CategorySetPattern", Universe=tuple(sorted(df["Body"].unique())))
    ABVPattern = psp.pattern_factory("ClosedIntervalPattern", BoundsUniverse=(10, 12, 13, 14, 16))

    class WinePattern(psp.bip.CartesianPattern):
        DimensionTypes = {
            "Type": TypePattern,
            "Country": CountryPattern,
            "ABV": ABVPattern,
            "Body": BodyPattern,
        }

    ps = psp.PatternStructure(WinePattern)
    ps.fit(df.to_dict("index"), min_atom_support=1)
    print("shape", ps.shape)

    concepts = ps.mine_concepts(min_support=1, min_delta_stability=0.01)
    print("concepts", len(concepts))

    implications = ps.mine_implications(min_support=1, basis_name="Canonical Direct")
    print("implications", len(implications))

    goal = set(df[df["Type"] == "Red"].index)
    subgroups = list(
        ps.iter_subgroups(
            goal_objects=goal,
            quality_measure="Precision",
            quality_threshold=0.6,
            max_length=2,
            min_support=1,
        )
    )
    print("subgroups", len(subgroups))


if __name__ == "__main__":
    main()

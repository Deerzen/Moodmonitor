import pandas as pd
import statsmodels.api as sm


def linear_regression(x, y, evaluations_length) -> float:
    """Simply takes two variables and the length of the evaluations list and calculates
    with a linear regression what the next value will most likely be. In case the
    calculated coefficients are statistically significant it returns the prediction.
    If they are not, a 0 is being returned."""

    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    coef = model.summary2().tables[1]["Coef."]
    prediction = round(coef[0] + coef[1] * (evaluations_length + 1), 2)
    if (
        model.summary2().tables[1]["P>|t|"][0] < 0.05
        and model.summary2().tables[1]["P>|t|"][1] < 0.05
    ):
        return prediction
    else:
        return 0


def create_dataset(last_evaluations, dimensions):
    formated_evaluations = {"pl": [], "at": [], "se": [], "ap": []}

    # Essentially adds the index numbers of the last evaluations to an array
    # and the values to the respective key in the formated_evaluations dictionary.
    evaluation_numbers = []
    for i in range(len(last_evaluations)):
        evaluation_numbers.append(i)
    for evaluation in last_evaluations:
        formated_evaluations["pl"].append(evaluation[0])
        formated_evaluations["at"].append(evaluation[1])
        formated_evaluations["se"].append(evaluation[2])
        formated_evaluations["ap"].append(evaluation[3])

    # The formatted data can now be transformed in a pandas dataframe for the
    # linear regression.
    df = pd.DataFrame(
        {
            "numbers": evaluation_numbers,
            dimensions[0]: formated_evaluations["pl"],
            dimensions[1]: formated_evaluations["at"],
            dimensions[2]: formated_evaluations["se"],
            dimensions[3]: formated_evaluations["ap"],
        }
    )
    return df


def classify_emotes(last_evaluations, needed_evaluations, dimensions) -> list:
    """Classifies the identified emotes using the four dimensions
    pleasentness, attention, sensitivity and aptitude and returns the predicted
    float values for all four dimensions in an array."""

    df = create_dataset(last_evaluations, dimensions)

    # Checks if the record of evaluations has enough data for linear regression.
    # If it does a linear regression is performed for every emotion dimension.
    # The outcomes are saved in the prediction variable.
    prediction = [0, 0, 0, 0]
    if len(last_evaluations) >= needed_evaluations:
        current_dimension = 0
        x = df[["numbers"]]
        for dimension in dimensions:
            y = df[dimension]
            dimension_prediction = linear_regression(x, y, len(last_evaluations))
            prediction[current_dimension] = dimension_prediction
            current_dimension += 1

    return prediction

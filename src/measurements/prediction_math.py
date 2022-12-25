import math
from typing import List


def calculate_mean_and_variance_online(
        prev_mean: float = 0.0,
        prev_variance: float = 0.0,
        prev_count: int = 0,
        new_value: float = 0.0) -> (float, float, int):
    """
    The method calculates mean and variance for each increment instead of all at once.
    See Welford's online algorithm
    """
    new_count = prev_count + 1
    delta = new_value - prev_mean
    new_mean = prev_mean + delta / new_count
    new_variance = prev_variance + delta * (new_value - new_mean)
    return new_mean, new_variance, int(new_count)


def calculate_standard_deviation(values: List[float]) -> float:
    """
    Calculates the standard deviation of a list of floats.
    See Welford's online algorithm
    """
    mean = 0
    variance = 0
    count = 0
    for x in values:
        count += 1
        delta = x - mean
        mean += delta / count
        variance += delta * (x - mean)
    if count <= 1:
        return 0
    return math.sqrt(variance / count)


def calculate_mean_online(prev_mean: float = 0.0, prev_count: int = 0, new_value: float = 0.0) -> (float, int):
    """
    The method calculates mean for each increment instead of all at once.
    See Welford's online algorithm
    """
    new_count = prev_count + 1
    delta = new_value - prev_mean
    new_mean = prev_mean + delta / int(new_count)
    return new_mean, int(new_count)


def calculate_mean(values: list) -> float:
    """
    Calculates the mean of a list of floats. See Welford's online algorithm
    See Welford's online algorithm
    """
    mean = 0
    count = 0
    for x in values:
        count += 1
        delta = x - mean
        mean += delta / count
    return mean


def calculate_probability_v1(
        age: int = 0,
        last_blood_pressure: float = 0.0,
        mean_respiratory_rate: float = 0.0,
        standard_deviation_temperature: float = 0.0
) -> float:
    """
    Calculates the probability of readmission for a patient. This formula is provided in the assignment
    :param age:
    :param last_blood_pressure:
    :param mean_respiratory_rate:
    :param standard_deviation_temperature:
    :return probability of readmission:
    """
    x_beta = -5 + 0.002 * age + 0.001 * last_blood_pressure + 0.03 * mean_respiratory_rate
    x_beta += 0.02 * standard_deviation_temperature
    return math.exp(x_beta) / (1 + math.exp(x_beta))

import logging
import numpy
import pandas
from mhcflurry import Class1AffinityPredictor, Class1NeuralNetwork
from mhcflurry.common import random_peptides
from mhcflurry.downloads import get_path

from mhcflurry.testing_utils import cleanup

logging.getLogger('tensorflow').disabled = True

PAN_ALLELE_PREDICTOR = None


def setup():
    global PAN_ALLELE_PREDICTOR
    PAN_ALLELE_PREDICTOR = Class1AffinityPredictor.load(
        get_path("models_class1_pan", "models.with_mass_spec"),
        max_models=4,
        optimization_level=0,)


def teardown():
    global PAN_ALLELE_PREDICTOR
    PAN_ALLELE_PREDICTOR = None
    cleanup()


def test_merge():
    assert len(PAN_ALLELE_PREDICTOR.class1_pan_allele_models) == 4

    peptides = random_peptides(100, length=9)
    peptides.extend(random_peptides(100, length=10))
    peptides = pandas.Series(peptides).sample(frac=1.0)

    alleles = pandas.Series(
        ["HLA-A*03:01", "HLA-B*57:01", "HLA-C*02:01"]
    ).sample(n=len(peptides), replace=True)

    predictions1 = PAN_ALLELE_PREDICTOR.predict(
        peptides=peptides, alleles=alleles)

    merged = Class1NeuralNetwork.merge(
        PAN_ALLELE_PREDICTOR.class1_pan_allele_models)
    merged_predictor = Class1AffinityPredictor(
        allele_to_sequence=PAN_ALLELE_PREDICTOR.allele_to_sequence,
        class1_pan_allele_models=[merged],
    )
    predictions2 = merged_predictor.predict(peptides=peptides, alleles=alleles)
    numpy.testing.assert_allclose(predictions1, predictions2, atol=0.1)

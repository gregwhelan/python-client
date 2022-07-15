import math

from tests.assets.plugins.taggers.plugin_trainable_tagger import TRAINING_PARAMETERS

from steamship.data.plugin import HostingType
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from tests import PLUGINS_PATH
from tests.utils.deployables import deploy_plugin
from tests.utils.fixtures import get_steamship_client


def test_get_training_parameters():
    """Any trainable plugin needs a Python+Lambda component that can report its trainable params.
    This tests that all the plumbing works for that to be returned"""
    client = get_steamship_client()
    tagger_path = PLUGINS_PATH / "taggers" / "plugin_trainable_tagger.py"
    # Now make a trainable tagger to train on those tags
    with deploy_plugin(
        client,
        tagger_path,
        "tagger",
        training_platform=HostingType.LAMBDA,
    ) as (tagger, taggerVersion, taggerInstance):
        training_request = TrainingParameterPluginInput(plugin_instance=taggerInstance.handle)
        res = taggerInstance.get_training_parameters(
            training_request
        )  # TODO (enias): How is this working?
        assert res.data is not None
        params = res.data

        assert params.training_epochs is not None
        assert params.training_epochs == TRAINING_PARAMETERS.training_epochs
        assert math.isclose(
            params.testing_holdout_percent,
            TRAINING_PARAMETERS.testing_holdout_percent,
            abs_tol=0.0001,
        )
        assert params.training_params == TRAINING_PARAMETERS.training_params

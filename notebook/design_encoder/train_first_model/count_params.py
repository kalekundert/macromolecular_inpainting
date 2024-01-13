import atompaint.transform_pred.models as apm
from torchinfo import summary

m = apm.FourierTransformationPredictor(
        conv_channels=[10, 20, 30, 40, 50],
        conv_field_of_view=[5, 3, 3, 3, 3],
        conv_stride=[2, 1, 1, 1, 1],
        mlp_channels=1,
        frequencies=2,
)

summary(m)


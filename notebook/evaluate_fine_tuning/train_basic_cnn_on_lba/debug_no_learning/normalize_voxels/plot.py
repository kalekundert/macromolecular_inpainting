import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import timerit

df = pl.read_parquet('voxels.parquet')

sns.displot(
        df.sample(1_000_000),
        x='value',
        hue='channel',
        kind='ecdf',
)

debug(df.group_by('channel').agg(
    pl.mean('value').alias('mean'),
    pl.median('value').alias('median'),
    pl.std('value').alias('std'),
    pl.min('value').alias('min'),
    pl.max('value').alias('max'),
).sort('channel'))

# sns.displot(
#         df.sample(1_000_000),
#         x='value',
#         hue='channel',
#         kind='hist',
#         binwidth=0.02,
#         element='poly',
#         fill=False,
# )
plt.show()



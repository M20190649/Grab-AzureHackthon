import vaex
import matplotlib.pyplot as plt

filename = r"/Users/fabian/CodingProject/git/AzureGrab/dataset/part-00007-8bbff892-97d2-4011-9961-703e38972569.c000.snappy.parquet"
data = vaex.open(filename)

data.plot_widget(data.rawlng, data.rawlat, shape = 512, limits = 'minmax', f = 'log1p', colormap = 'plasma')

df_filtered.plot('pickup_longitude', 'pickup_latitude', what='mean(fare_over_distance)',
                 colormap='plasma', f='log1p', shape=512, colorbar=True, 
                 colorbar_label='mean fare/distance [$/mile]', vmin=0.75, vmax=2.5)
                 
# data.plot(data.rawlng, data.lawlat, what = "mean(hour_of daya)", colorbar_label = "demand (x)"colorbar = True, colormap = cm_plusmin)
# plt.show()
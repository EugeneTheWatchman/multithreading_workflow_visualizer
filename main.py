from logreader import LogReader
from diagramplotter import DiagramPlotter

if __name__ == "__main__":
    folder_with_logs = "milli"
    logReader = LogReader(folder_with_logs)
    plotter = DiagramPlotter(logReader, 5)
    plotter.plot()



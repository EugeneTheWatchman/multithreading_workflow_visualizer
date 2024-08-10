from logreader import LogReader
from diagramplotter import DiagramPlotter





if __name__ == "__main__":
    logReader = LogReader("milli")
    plotter = DiagramPlotter(logReader, 5)
    plotter.plot()



from logreader import LogReader
from diagramplotter import DiagramPlotter

if __name__ == "__main__":
    folder_with_logs = "milli"
    logReader = LogReader(folder_with_logs)

    process_color_maper = {
        'SYNC': 'r',
        'WORK': 'b'
    }
    plotter = DiagramPlotter(logReader, process_color_maper, 5)
    plotter.draw_all()

    logReader.close_files()



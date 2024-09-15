import sys
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import matplotlib.font_manager as font_manager
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#use backend Agg for non-interactive plot
class ShotVisualizer:
    def __init__(self, csv_path, font_path):
        # Load the data
        self.df = pd.read_csv(csv_path)
        
        # Font properties
        self.font_props = font_manager.FontProperties(fname=font_path)
        
        # Scaling coordinates to 1-100 for plotting
        self.df['X'] = self.df['X'] * 100
        self.df['Y'] = self.df['Y'] * 100
        
        # Pitch setup
        self.pitch = VerticalPitch(
            pitch_type='opta', 
            half=True, 
            pitch_color='#0C0D0E', 
            pad_bottom=.5, 
            line_color='white',
            linewidth=.75,
            axis=True, 
            label=True
        )
        
        # Calculate the main statistics
        self.calculate_stats()
    
    def calculate_stats(self):
        # General statistics
        self.total_shots = self.df.shape[0]
        self.total_goals = self.df[self.df['result'] == 'Goal'].shape[0]
        self.total_xG = self.df['xG'].sum()
        self.xG_per_shot = self.total_xG / self.total_shots
        
        # Average distance calculations
        self.points_average_distance = self.df['X'].mean()
        self.actual_average_distance = 120 - (self.df['X'] * 1.2).mean()
        
        # Shot types
        self.right_foot_shots = self.df[self.df['shotType'] == 'RightFoot'].shape[0]
        self.left_foot_shots = self.df[self.df['shotType'] == 'LeftFoot'].shape[0]
        self.head_shots = self.df[self.df['shotType'] == 'Head'].shape[0]
        self.other_shots = self.df[self.df['shotType'] == 'OtherBodyPart'].shape[0]
    
    def plot_visualization(self):
        # Create figure with more proportional dimensions (larger height to avoid stretching)
        fig = plt.figure(figsize=(10, 14))
        fig.patch.set_facecolor('#0C0D0E')
        
        # Top Text
        ax1 = fig.add_axes([0.05, 0.75, 0.9, .2])  # Adjusted to fit better in the layout
        ax1.set_facecolor('#0C0D0E')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.text(0.5, .85, 'Erling Haaland', fontsize=20, fontproperties=self.font_props, fontweight='bold', color='white', ha='center')
        ax1.text(0.5, .7, 'All shots in the Premier League 2022-23', fontsize=14, fontweight='bold', fontproperties=self.font_props, color='white', ha='center')
        ax1.set_axis_off()
        
        # Pitch
        ax2 = fig.add_axes([.05, 0.25, .9, .5])  # Kept larger to better display the pitch
        ax2.set_facecolor('#0C0D0E')
        self.pitch.draw(ax=ax2)
        
        # Average distance line
        ax2.scatter(90, self.points_average_distance, s=100, color='white', linewidth=.8)
        ax2.plot([90, 90], [100, self.points_average_distance], color='white', linewidth=2)
        ax2.text(90, self.points_average_distance - 4, f'Average Distance\n{self.actual_average_distance:.1f} yards', fontsize=10, fontproperties=self.font_props, color='white', ha='center')
        
        # Plot each shot
        for shot in self.df.to_dict(orient='records'):
            self.pitch.scatter(
                shot['X'], shot['Y'], 
                s=300 * shot['xG'], 
                color='red' if shot['result'] == 'Goal' else '#0C0D0E', 
                ax=ax2,
                alpha=.7,
                linewidth=.8,
                edgecolor='white'
            )
        ax2.set_axis_off()

        # Bottom stats
        self.plot_stats(fig)

        return fig

    def plot_stats(self, fig):
        # Stats below pitch
        ax3 = fig.add_axes([0.05, .15, 0.9, .05])  # Adjusted layout for stats
        ax3.set_facecolor('#0C0D0E')
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        
        ax3.text(0.25, .5, 'Shots', fontsize=20, fontproperties=self.font_props, fontweight='bold', color='white', ha='left')
        ax3.text(0.25, 0, f'{self.total_shots}', fontsize=16, fontproperties=self.font_props, color='red', ha='left')

        ax3.text(0.38, .5, 'Goals', fontsize=20, fontproperties=self.font_props, fontweight='bold', color='white', ha='left')
        ax3.text(0.38, 0, f'{self.total_goals}', fontsize=16, fontproperties=self.font_props, color='red', ha='left')

        ax3.text(0.53, .5, 'xG', fontsize=20, fontproperties=self.font_props, fontweight='bold', color='white', ha='left')
        ax3.text(0.53, 0, f'{self.total_xG:.2f}', fontsize=16, fontproperties=self.font_props, color='red', ha='left')

        ax3.text(0.63, .5, 'xG/Shot', fontsize=20, fontproperties=self.font_props, fontweight='bold', color='white', ha='left')
        ax3.text(0.63, 0, f'{self.xG_per_shot:.2f}', fontsize=16, fontproperties=self.font_props, color='red', ha='left')

        ax3.set_axis_off()

        # Shot types (right side)
        ax4 = fig.add_axes([0.85, .25, .15, .5])  # Adjusted to fit the right-hand stats better
        ax4.set_facecolor('#0C0D0E')
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)

        ax4.text(0.0, .85, 'Right Foot', fontsize=20, fontproperties=self.font_props, fontweight='bold', color='white', ha='center')
        ax4.text(0.0, .8, f'{self.right_foot_shots}', fontsize=16, fontproperties=self.font_props, color='red', ha='center')

        ax4.text(0.0, .65, 'Left Foot', fontsize=20, fontproperties=self.font_props, fontweight='bold', color='white', ha='center')
        ax4.text(0.0, .6, f'{self.left_foot_shots}', fontsize=16, fontproperties=self.font_props, color='red', ha='center')

        ax4.text(0.0, .45, 'Head', fontsize=20, fontproperties=self.font_props, fontweight='bold', color='white', ha='center')
        ax4.text(0.0, .4, f'{self.head_shots}', fontsize=16, fontproperties=self.font_props, color='red', ha='center')

        ax4.text(0.0, .25, 'Other', fontsize=20, fontproperties=self.font_props, fontweight='bold', color='white', ha='center')
        ax4.text(0.0, .2, f'{self.other_shots}', fontsize=16, fontproperties=self.font_props, color='red', ha='center')

        ax4.set_axis_off()



class Window(QWidget):
    def __init__(self, font_path):
        super().__init__()
        self.initUI()
        self.font_path = font_path

    def initUI(self):
        self.setWindowTitle('Shot Visualizer')
        self.setGeometry(100, 100, 800, 600)
        
        # Layout
        layout = QVBoxLayout()
        
        # Label
        self.label = QLabel('Load a CSV file to generate shot visualizations')
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        # Load Button
        self.load_button = QPushButton('Load CSV File', self)
        self.load_button.clicked.connect(self.openFileNameDialog)
        layout.addWidget(self.load_button)
        
        # Canvas for matplotlib plot
        self.canvas = None
        
        self.setLayout(layout)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)
        if file_name:
            try:
                self.label.setText(f"Loaded: {file_name}")
                self.load_csv_and_plot(file_name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file: {e}")

    def load_csv_and_plot(self, file_name):
        # Create visualizer and plot
        visualizer = ShotVisualizer(file_name, self.font_path)
        fig = visualizer.plot_visualization()

        # Remove the existing canvas
        if self.canvas:
            self.layout().removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.canvas = None
        
        # Create a new canvas
        self.canvas = FigureCanvas(fig)
        self.layout().addWidget(self.canvas)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    font_path = r'C:\Users\haida\Documents\Python Scripts\Athletic Graphs\Arvo\Arvo-Regular.ttf'
    window = Window(font_path)
    window.show()

    sys.exit(app.exec_())

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

class DataAnalyzer:

    def __init__(self):
        self.df = None
        args = sys.argv[1:]
        # self.folder_path = "C:\\Users\\Kamo\\Desktop\\testBuild\\Test\\Dodgeball\\Logs\\PlayerData\\" # args[0] # Change to folder path
        self.folder_path = "Assets/Dodgeball/Logs/PlayerData/"
        self.filename = ""

    def read_data(self):
        self.df = pd.read_csv(self.folder_path+self.filename)

    def save_data(self):
        file_dest = self.folder_path+"clean/"
        if not os.path.exists(file_dest):
            os.makedirs(file_dest)
        print(file_dest+self.filename)
        self.df.to_csv(path_or_buf=file_dest+self.filename)

    def print_data(self):
        print(self.df)

    def print_duration(self):
        seconds = self.df.elapsed_time.max()
        minutes = int(seconds / 60)
        rest_seconds = seconds % 60
        print("TOTAL TIME OF LOG: "+str(seconds) + " seconds (" + str(minutes) + " min " + str(round(rest_seconds, 2)) + " seconds)\n")

    def clean_data(self):
        """
        Remove the logs before S, so S is the starting point.
        Convert from timestamp to elapsed time since start.
        :return:
        """
        # convert the TimeStamp column to a datetime format
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'], format='%H:%M:%S.%f')

        # Find S elapsed time
        s_elapsed = self.df.loc[self.df.EventType == "S", "Timestamp"].min()

        # Select subset of DataFrame where Timestamp is greater than or equal to s_elapsed
        self.df = self.df[self.df['Timestamp'] >= s_elapsed]

        # Elapsed time column
        self.df['elapsed_time'] = (self.df['Timestamp'] - self.df['Timestamp'].min()).dt.total_seconds()

        # Remove old timestamp
        self.df = self.df.drop(['Timestamp'], axis=1)

        # Move elapsed to start.-----------------
        # Get the last column using iloc
        last_column = self.df.iloc[:, -1]

        # Remove the last column from the DataFrame
        self.df = self.df.iloc[:, :-1]

        # Concatenate the last column to the front of the DataFrame
        self.df = pd.concat([last_column, self.df], axis=1)


    # def print_corner(self):
    #    corner_points = self.df[self.df.Corner != 0]
    #    print("There was " + str(len(corner_points)) + "/" + str(
    #        len(self.df)) + " entries where the agent was in the corner")
    #    print(corner_points)

    def plot(self, columns=None):
        if columns is None:
            # columns = ['BallsLeft', 'PlayerLives', 'EnemyLives', 'Corner']
            columns = ['BlueBallsLeft', 'PurpleBallsLeft', 'BlueLives', 'PurpleLives']

        df_copy = self.df.copy()

        # set the TimeStamp column as the index
        df_copy.set_index('elapsed_time', inplace=True)
        # df_copy.set_index('Timestamp', inplace=True)

        # create the figure and axes objects
        fig, ax = plt.subplots()

        # plot the BallsLeft, PlayerLives, EnemyLives, and Corner columns
        df_copy[columns].plot(ax=ax)

        # set the title and labels for the plot
        if len(columns) == 1:
            ax.set_title(columns[0])
        else:
            ax.set_title('GameLog')
        ax.set_xlabel('Time (S)')
        ax.set_ylabel('Count')

        # show the plot
        plt.show()

    def elapsed_time(self, column="BlueLives"):
        # Create a boolean mask where LivesLeft equals 3
        # if column == "Corner":
        #    text = "condition happens"
        if column == "BlueLives":
            text = "is equal to 3"
        elif column == "PurpleLives":
            text = "is equal to 3"
        elif column == "BlueBallsLeft":
            text = "is equal to 4"
        elif column == "PurpleBallsLeft":
            text = "is equal to 4"
        else:
            text = "is something"

        def logic_op(row, boolean_mode):
            if boolean_mode == True:
                if column == "BlueLives":     # Duration the player had 3 lives
                    return True if row[column] == 3 else False
                if column == "PurpleLives":       # Duration enemy had 3 lives
                    return True if row[column] == 3 else False
                if column == "BlueBallsLeft":       # Duration player had 4 balls
                    return True if row[column] == 4 else False
                if column == "PurpleBallsLeft":     # Duration player had 4 balls
                    return True if row[column] == 4 else False
                # if column == "Corner":          # Duration opponent spent in the corner
                #    return True if row[column] > 0 else False
            else:
                if column == "BlueLives":     # Duration the player had 3 lives
                    return True if row[column] != 3 else False
                if column == "PurpleLives":       # Duration enemy had 3 lives
                    return True if row[column] != 3 else False
                if column == "BlueBallsLeft":       # Duration player had 4 balls
                    return True if row[column] != 4 else False
                if column == "PurpleBallsLeft":     # Duration player had 4 balls
                    return True if row[column] != 4 else False
                # if column == "Corner":          # Duration opponent spent in the corner
                #    return True if row[column] == 0 else False

        # Loop through DataFrame and calculate duration of each sequence of LivesLeft being 3
        in_sequence = False
        sequence_start = None
        total_duration = pd.Timedelta(0).total_seconds()
        for i, row in self.df.iterrows():
            if logic_op(row, True) and not in_sequence:
                # Start of new sequence
                in_sequence = True
                sequence_start = row['elapsed_time']
            elif logic_op(row, False) and in_sequence:
                # End of sequence
                in_sequence = False
                sequence_end = row['elapsed_time']
                sequence_duration = sequence_end - sequence_start
                total_duration += sequence_duration

        # print(f'Total seconds that '+str(column)+' '+text+': '+str(total_duration.total_seconds()))
        print(f'Total seconds that '+str(column)+' '+text+': '+str(round(total_duration, 3)))
    

    def count_event_occurences(self, event):
        return self.df['EventType'].value_counts()[event]
    
    
    def calculate_precision(self, player):
        precision = None
        if player == 'Blue':
            precision = self.count_event_occurences('HitPurple')/self.count_event_occurences('BlueThrewBall')
        elif player == 'Purple':
            precision = self.count_event_occurences('HitBlue')/self.count_event_occurences('PurpleThrewBall')
        return precision
    

    def print_event_count(self, event='BlueThrewBall'):
        count = self.count_event_occurences(event)
        print(f'{event} occurred {count} times')
    

    def print_precision(self, player='Blue'):
        precision = self.calculate_precision(player)
        print(f'{player} had a precision of {round(precision * 100, 2)} %')


if __name__ == "__main__":
    da = DataAnalyzer()

    # Iterate over all files in the folder
    for filename in os.listdir(da.folder_path):
        # Check if the item is a file (as opposed to a directory)
        if os.path.isfile(os.path.join(da.folder_path, filename)):
            # Print the name of the file
            da.filename = filename
            # print(filename)
            if ".meta" not in filename:
                da.read_data()
                da.clean_data()
                da.print_duration()
                da.save_data()


    da.print_data()
    # da.print_corner()

    # da.plot(columns=['BlueLives'])
    # da.plot(columns=['PurpleLives'])
    # da.plot(columns=['BlueBallsLeft'])
    # da.plot(columns=['PurpleBallsLeft'])
    # da.plot(columns=['Corner'])

    # Elapsed time prints (total duration a given field is a given condition)
    da.elapsed_time(column="BlueLives")
    da.elapsed_time(column="PurpleLives")
    da.elapsed_time(column="BlueBallsLeft")
    da.elapsed_time(column="PurpleBallsLeft")
    # da.elapsed_time(column="Corner")

    print()

    # Count event prints how many times each event occurs
    da.print_event_count(event="BluePickedUpBall")
    da.print_event_count(event="PurplePickedUpBall")
    da.print_event_count(event="BlueThrewBall")
    da.print_event_count(event="PurpleThrewBall")
    da.print_event_count(event="HitBlue")
    da.print_event_count(event="HitPurple")

    print()

    # Precision
    da.print_precision(player="Blue")
    da.print_precision(player="Purple")


class Human:
    def __init__(self, id, bounding_box, histogram):
        self.id = id
        self.current_position = bounding_box
        self.untracked_frame_counter = 0
        self.histogram = histogram
        print('new human was created at position {}'.format(bounding_box))

    def get_id(self):
        return self.id

    def get_untracked_frame_counter(self):
        return self.untracked_frame_counter

    def increase_untracked_frame_counter(self):
        self.untracked_frame_counter = self.untracked_frame_counter + 1

    def update_position(self, new_position):
        self.current_position = new_position
        self.untracked_frame_counter = 0

    def get_current_position(self):
        return self.current_position

    def get_histogram(self):
        return self.histogram

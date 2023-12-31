import os
import tensorflow as tf
# import tensorflow_datasets as tfd
from sklearn.model_selection import train_test_split

# DataReader, a class build to read data into Tensorflow datasets
# This code partially follows Kevin Kibe's tutorial on Deep learning for Image Segmentation with Tensorflow.
# Linked here: https://www.analyticsvidhya.com/blog/2023/04/deep-learning-for-image-segmentation-with-tensorflow/#Defining_and_Building_the_Model
class DataReader:
    def __init__(self, X_path, y_path):
        # Paths
        self.X_train_masterpath = X_path
        self.y_train_masterpath = y_path
        self.X_paths = None
        self.y_paths = None
        # Data:
        self.train_ds = None
        self.val_ds = None
        self.image_size = (1024, 1024)

    # Get a list of all filenames that we want.
    # @RETURNS: list_X, list_y --- both are lists of strings.
    def get_file_lists(self, train_X_masterpath = None, train_y_masterpath = None):
        # Ensure we have paths:
        if train_X_masterpath == None:
            train_X_masterpath = self.X_train_masterpath
        if train_y_masterpath == None:
            train_y_masterpath = self.y_train_masterpath
        # a list to collect paths of 1000 images
        train_X_paths = []
        X_paths_raw = os.walk(train_X_masterpath)
        for root, dirs, files in X_paths_raw:
            # iterate over 1000 images
            for file in files:
                # create path
                path = os.path.join(root,file)
                # Check to see if it's a pre-disaster picture
                if "pre" not in path:
                    continue
                # add path to list
                train_X_paths.append(path)
        # a list to collect paths of 1000 images
        train_y_paths = []
        y_paths_raw = os.walk(train_y_masterpath)
        for root, dirs, files in y_paths_raw:
            # iterate over 1000 images
            for file in files:
                # create path
                path = os.path.join(root,file)
                # Check to see if it's a pre-disaster picture AND to make sure it matches an input file:
                if "pre" not in path or f"{train_X_masterpath}" "\\" + path.split('\\')[-1][0:-11]+".png" not in train_X_paths:
                    continue
                # add path to list
                train_y_paths.append(path)

        # Sort the data so each point is in the same position:
        train_X_paths.sort()
        train_y_paths.sort()
        # Finalize:
        assert(len(train_X_paths) == len(train_y_paths))
        print(f"---\nX : {len(train_X_paths)} files | y: {len(train_y_paths)} files\n---")
        self.X_paths = train_X_paths
        self.y_paths = train_y_paths
        return train_X_paths, train_y_paths
    
    # Get a list of all filenames that we want. (Colab/Mac version)
    # @RETURNS: list_X, list_y --- both are lists of strings.
    def get_file_lists_colab(self, train_X_masterpath = None, train_y_masterpath = None):
        # Ensure we have paths:
        if train_X_masterpath == None:
            train_X_masterpath = self.X_train_masterpath
        if train_y_masterpath == None:
            train_y_masterpath = self.y_train_masterpath
        # a list to collect paths of 1000 images
        train_X_paths = []
        X_paths_raw = os.walk(train_X_masterpath)
        for root, dirs, files in X_paths_raw:
            # iterate over 1000 images
            for file in files:
                # create path
                path = os.path.join(root,file)
                # Check to see if it's a pre-disaster picture
                if "pre" not in path:
                    continue
                # add path to list
                train_X_paths.append(path)
        # a list to collect paths of 1000 images
        train_y_paths = []
        y_paths_raw = os.walk(train_y_masterpath)
        for root, dirs, files in y_paths_raw:
            # iterate over 1000 images
            for file in files:
                # create path
                path = os.path.join(root,file)
                # Check to see if it's a pre-disaster picture AND to make sure it matches an input file:
                if "pre" not in path or f"{train_X_masterpath}/{path.split('/')[-1][0:-11]}.png" not in train_X_paths:
                    continue
                # add path to list
                train_y_paths.append(path)
        # Sort the data so each point is in the same position:
        train_X_paths.sort()
        train_y_paths.sort()
        # Finalize:
        assert(len(train_X_paths) == len(train_y_paths) and len(train_X_paths) != 0)
        print(f"---\nX : {len(train_X_paths)} files | y: {len(train_y_paths)} files\n---")
        
        self.X_paths = train_X_paths
        self.y_paths = train_y_paths
        return train_X_paths, train_y_paths
    
    # Turn the data into Tensorflow Datasets.
    # @SPECIAL PARAMS: test_data --- boolean, tells us if the method should split the data into train/val
    # @RETURNS: test_data == True : train, val --- TF datasets
    # @RETURNS: test_data == False: test, test_X, test_y --- TF datasets, test is zipped from the latter two.
    def get_tf_data(self, X_paths = None, y_paths = None, new_size = None, desired_amount = None, test_data=False):
        # Ensure we have paths:
        if X_paths == None:
            X_paths = self.X_paths
        if y_paths == None:
            y_paths = self.y_paths
        if desired_amount == None:
            desired_amount = len(X_paths)
        # Get tf object from each file:
        # Next, turn the files into points:
        X = []
        y = []

        for i in range(desired_amount): # WE RUN OUT OF RAM REALLY QUICKLY ON THIS...
            # Get the corresponding files:
            file_X = tf.io.read_file(X_paths[i])
            file_y = tf.io.read_file(y_paths[i])

            # Decode them into data:
            X.append(tf.image.decode_png(file_X, channels=3, dtype=tf.uint8))
            y.append(tf.image.decode_png(file_y, channels=1, dtype=tf.uint8))
        # Resizing:
        if new_size != None:
            X = [self.resize_image(i, new_size) for i in X]
            y = [self.resize_mask(m, new_size) for m in y]
            self.size = new_size
        
        if not test_data:
            train_X, val_X, train_y, val_y = train_test_split(X, y, test_size=0.2, random_state=0)
            print(f"---\n{len(train_X)} in train | {len(val_X)} in val\n---")
            self.train_ds = tf.data.Dataset.from_tensor_slices((train_X, train_y))
            self.val_ds = tf.data.Dataset.from_tensor_slices((val_X, val_y))
            return self.train_ds, self.val_ds
        train_X = X
        train_y = y
        print(f"---\n{len(train_X)} loaded\n---")
        test_ds = tf.data.Dataset.from_tensor_slices((train_X, train_y))
        test_X = tf.data.Dataset.from_tensor_slices(train_X)
        test_y = tf.data.Dataset.from_tensor_slices(train_y)
        
        return test_ds, test_X, test_y
    
    # Although this function is mine, all data augmentation functions are Kevin Kibe's.
    def augment(self, train_ds):
        # Augment the data:
        horiz = train_ds.map(self.flip_hori)
        vert = train_ds.map(self.flip_vert)
        rot = train_ds.map(self.rotate)
        bright = train_ds.map(self.brightness)
        gamma = train_ds.map(self.gamma)
        hue = train_ds.map(self.hue)
        # Concatenate:
        train_ds = train_ds.concatenate(horiz)
        train_ds = train_ds.concatenate(vert)
        train_ds = train_ds.concatenate(rot)
        train_ds = train_ds.concatenate(bright)
        train_ds = train_ds.concatenate(gamma)
        train_ds = train_ds.concatenate(hue)
        return train_ds

    def resize_image(self, image, size = (128,128)):
        # scale the image
        image = tf.cast(image, tf.float32)
        image = image/255.0
        # resize image
        image = tf.image.resize(image, size)
        return image

    def resize_mask(self, mask, size = (128,128)):
        # resize the mask
        mask = tf.image.resize(mask, size)
        mask = tf.cast(mask, tf.float32) ############## WAS UINT8
        return mask

    def brightness(self, img, mask):
        img = tf.image.adjust_brightness(img, 0.1)
        return img, mask

    # adjust gamma of image
    # don't alter in mask
    def gamma(self, img, mask):
        img = tf.image.adjust_gamma(img, 0.1)
        return img, mask

    # adjust hue of image
    # don't alter in mask
    def hue(self, img, mask):
        img = tf.image.adjust_hue(img, -0.1)
        return img, mask

    def crop(self, img, mask):
        # crop both image and mask identically
        img = tf.image.central_crop(img, 0.7)
        # resize after cropping
        img = tf.image.resize(img, (128,128))
        mask = tf.image.central_crop(mask, 0.7)
        # resize afer cropping
        mask = tf.image.resize(mask, (128,128))
        # cast to integers as they are class numbers
        mask = tf.cast(mask, tf.float32) ################# WAS UINT8
        return img, mask
    # flip both image and mask identically
    def flip_hori(self, img, mask):
        img = tf.image.flip_left_right(img)
        mask = tf.image.flip_left_right(mask)
        return img, mask

    # flip both image and mask identically
    def flip_vert(self, img, mask):
        img = tf.image.flip_up_down(img)
        mask = tf.image.flip_up_down(mask)
        return img, mask

    # rotate both image and mask identically
    def rotate(self, img, mask):
        img = tf.image.rot90(img)
        mask = tf.image.rot90(mask)
        return img, mask

# Just a shorthand method to automate grabbing our training and validation data.
# @RETURNS: train, val --- both tf dtasets zipped from X,y values
def default_method(desired_amount = None):
    train_X_masterpath = "data/train/images"
    train_y_masterpath = "data/train/targets"
    # Get data:
    dr = DataReader(train_X_masterpath, train_y_masterpath)
    # dr.get_file_lists()
    dr.get_file_lists_colab()
    train, val = dr.get_tf_data(new_size = (256, 256), desired_amount=desired_amount)

    AT = tf.data.AUTOTUNE
    #buffersize
    BUFFER = 1000
    BATCH = 32

    train = dr.augment(train)
    train = train.cache().shuffle(BUFFER).batch(BATCH).repeat()
    train = train.prefetch(buffer_size=AT)
    val = val.batch(BATCH)

    return train, val

# Demo:            
if __name__ == "__main__":
    dr = DataReader("data/train/images", "data/train/targets")
    one, two = dr.get_file_lists()
    three, four = dr.get_tf_data()
    print(type(three), "\n", type(four))
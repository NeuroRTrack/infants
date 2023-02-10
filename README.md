# Infants Project

The project aims at analysing preterm infants polysomnography data to extract useful information about sleep cycle and EEG metrics.

## Dataset
The dataset contains 37 subjects, with two recording sessions each of approximately 34 weeks and 40 weeks gestational age. A single session is expected to contain about 24 hours of recording.

> Note that almost all subjects present gaps or fewer recording hours, some of them only one session (either 34 weeks or 40 weeks).

Each recording session is subdivided into several subsequent `.edf` files, denominated runs. For every run, a correspondent hypnogram `.txt` file is available.

The dataset is organized in compliance with the [BIDS protocol](https://bids-specification.readthedocs.io/en/stable/) to ensure a functional storage of the data.

Finally, a `lookup_table.xlsx` file contains all the personal information about the subjects and additional cues about the dataset structure and missing data. Such file is protected by a password for security and privacy reasons.
## Code
The code is written in `Python 3.10` and the usage of `Anaconda` is warmly suggested in order to employ an isolated environment. The `infants.yaml` file provided in this repository can be used to automatically generate a `conda` environment with all the required modules and packages.

When running any experiment or pipeline, the settings - i.e., subjects, sessions, dataset path, ... - are automatically retrieved from the `settings.json` file located in the main directory.

All the produced outputs are saved into the `output` directory, following a folder tree similar to the dataset one.

Several modules listed below are used to analyse the data. However, the code should be run by `.ipynb` interactive Python notebooks.

### Hypnograms
The `hyp` module contains all the code necessary to extract the annotations provided in the `.txt` files. 
After producing some generic statistics about sleep and wake stages, a `.csv` file with the preprocessed annotations is saved. Such file is formatted in compliance with the EEG annotations format for the [MNE](https://github.com/mne-tools/mne-python) library.

### EEG
The `eeg` module loads the `.edf` files as specified in `settings.json` and superimposes the previously generated sleep stage annotations.
Then it performs some generic preprocessing an data harmonization.
The PSD is extracted for each hypnogram stage.
Finally, it allows to compute a number of metrics, for instance the PLV.
In order to assess the meaningfulness of the PLV, surrogates are employed.
> Note that PLV computation and surrogates are currently work in progress.

### Visualization
The `visualization` module contains all the functions necessary to build plots and graphics. It strongly relies on the [Matplotlib](https://matplotlib.org/) library.
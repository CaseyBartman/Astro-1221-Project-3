# Astro-1221-Project-3

Command to install packages: 
**$ pip install streamlit, pandas, scipy**



# Scientific Bibliography:
### Tripp Relation:  

This is the exact empirical method used to prove Type Ia Supernovae are standardizable. It introduces the light-curve stretch and color corrections, and we use it in the **SupernovaCosmologyModels** class

1) Tripp, R. (1998). "A two-parameter luminosity correction for Type Ia supernovae," Astronomy and Astrophysics, 331, 815-820 https://ui.adsabs.harvard.edu/abs/1998A%26A...331..815T/abstract 

2) Section 1.1 "The Tripp Formula" of this source provided us the formula implemented in **SupernovaCosmologyModels.calculate_distance_modulus()**

    Mandel, K. S., Scolnic, D. M., Shariff, H., Foley, R. J., & Kirshner, R. P. (2017). The Type Ia supernova color–magnitude relation and host galaxy dust: A simple hierarchical Bayesian model. The Astrophysical Journal, 842(2), 93. https://doi.org/10.3847/1538-4357/aa6038

### Advanced Cosmological Distance Integral:

This is the standard cosmography integral used to calculate lumninosity distance in an expanding universe that contains both matter AND dark energy. We use it in the **SupernovaCosmologyModels** class: dL = (1 + z) x (comoving distance) with this source (formula 15 in this source)

1) Hogg, D. W. (1999). Distance measures in cosmology. arXiv preprint: https://arxiv.org/abs/astro-ph/9905116

### Supernova Dataset (Union2.1 Compilation)

This is the compilation set that we used to grab the supernova data. We'll cite both the JSON source and the original team who compiled and cleaned the dataset

1) Suzuki, N., et al. (The Supernova Cosmology Project) (2012). The Hubble Space Telescope Cluster Supernova Survey: V. Improving the Dark Energy Constraints Above z>1 and Building an Early-type-hosted Supernova Sample. The Astrophysical Journal, 746(1), 85. https://arxiv.org/abs/1105.3470

2) The previous source links to this project: https://supernova.lbl.gov/Union/ We used a subset compilation formatted for easier parsing here: https://datarepository.wolframcloud.com/resources/Type-Ia-Supernova-Data/
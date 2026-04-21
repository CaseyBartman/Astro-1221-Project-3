# Astro-1221-Project-3

### Command to install packages: 
**$ pip install streamlit, pandas, scipy**

### App instructions:
To run the app:
**$ streamlit run app.py**

# Project Goal:
To fit the relationship between supernova distance, redshift, and measure the universe's expansion. We load MANY supernovae with measured values and implement the Hubble law model, fitting appropriately with the Hubble constants and plotting everything via streamlit. 

See requirements.txt for more information on class architecture and other file structure information.

# Scientific Bibliography:
### Tripp Relation:  

This is the exact empirical method used to prove Type Ia Supernovae are standardizable. It introduces the light-curve stretch and color corrections, and we use it in the **SupernovaCosmologyModels** class

1) Tripp, R. (1998). "A two-parameter luminosity correction for Type Ia supernovae," Astronomy and Astrophysics, 331, 815-820 https://ui.adsabs.harvard.edu/abs/1998A%26A...331..815T/abstract 

2) Section 1.1 "The Tripp Formula" of this source provided us the formula implemented in **SupernovaCosmologyModels.calculate_distance_modulus()**

    Mandel, K. S., Scolnic, D. M., Shariff, H., Foley, R. J., & Kirshner, R. P. (2017). The Type Ia supernova color–magnitude relation and host galaxy dust: A simple hierarchical Bayesian model. The Astrophysical Journal, 842(2), 93. https://doi.org/10.3847/1538-4357/aa6038

### Advanced Cosmological Distance Integral:

This is the standard cosmography integral used to calculate lumninosity distance in an expanding universe that contains both matter AND dark energy. We use it in the **SupernovaCosmologyModels** class: dL = (1 + z) x (comoving distance) with this source (formula 15 in this source)

1) Hogg, D. W. (1999). Distance measures in cosmology. arXiv preprint: https://arxiv.org/abs/astro-ph/9905116

### Supernova Dataset (JLA Compilation)

This is the compilation set that we used to grab the supernova data. We retreived the data from the Wolfram Data
Repository. This repository hosts JLA, we initially looked at data from Union2.1 but determined that it would be better to work with about 150 more supernovae. The larger sample size produces better science results. Using the 580 in Union2.1 would make our error bars bigger simply to match a specific historical complilation. Both complilations are essentially the same, but a larger set would produce better results for us to prove the findings of the Nobel Prize winners.

1) Fix citation for JLA Detoule et al. 2014 arXiv:1401.4064

2) The orginal source of Union links to: https://supernova.lbl.gov/Union/ We used a subset compilation formatted for easier parsing here: https://datarepository.wolframcloud.com/resources/Type-Ia-Supernova-Data/


## AI Usage in Project:
- Casey: 
 - I used AI a bit more in this project compared to others, mainly to help fill in the gaps of my astronomical knowledge. In terms of the implementation details and architectural decisions for essentially the entire projectr, I did those myself. I only use LLMs and agentic coding to help with "busywork" boilerplate tasks, so having it help with the documentation was extremely useful- especially because I wasn't very familiar with the astronomical context behind this project. I did use it to help double check with the sources and make sure my formulas that were used were accurate and well implemented. 

- Lauren:
 - I also used a little bit more in this project for the tecnical set up for my code. I understood what I did for my last streamlit code, but I did not like how clunky it felt and I wanted a different way to structure my code. I was able to come up with a clear vision of how I wanted the pages of the app to look and some of the funtions needed to execute them. I used the Cursor assistant to create larger blocks of code as well as generate some of the larger blocks of description seen in the app. Any and all documentation explaining the is all me. I was able to do the astrophysical aspects of the project using old notes and textbooks with the occansional google of what an equation means. 
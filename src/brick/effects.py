import numpy as np
from . import utility
from .parameter import TargetThickness
from .constants import *


class Effect:
    def __init__(self, row, index) -> None:
        self.row = row.split()
        self.include = (int(self.row[EFFECT_INCLUDE_INDEX]) == 1)
        self.segments_indexes = self.row[EFFECTS_SEGMENTS_INDEX][1:-1] # not used at the moment
        self.integration_points = int(self.row[EFFECTS_INTEGRATION_POINTS])
        self.include_gaussian_convolution = (int(self.row[EFFECTS_INCLUDE_GAUSSIAN_CONVOLUTION]) == 1)
        self.gaussian_convolution_sigma = float(self.row[EFFECTS_GAUSSIAN_CONVOLUTION_SIGMA])
        self.include_target_integration = (int(self.row[EFFECTS_INCLUDE_TARGET_INTEGRATION]) == 1)
        self.target_thickness = float(self.row[EFFECTS_TARGET_THICKNESS])
        self.stopping_crosssection = self.row[EFFECTS_STOPPING_CROSSSECTION] # not used at the moment
        self.stopping_crosssection_n_par = int(self.row[EFFECTS_STOPPING_CROSSSECTION_N_PAR])
        self.stopping_crosssection_par = []
        for i in range(self.stopping_crosssection_n_par):
            self.stopping_crosssection_par.append(float(self.row[EFFECTS_STOPPING_CROSSSECTION_N_PAR + i + 1]))
        self.include_att_coeffs = (int(self.row[EFFECTS_STOPPING_CROSSSECTION_N_PAR + i + 2]) == 1) #not used at the moment
        self.att_coeffs = self.row[EFFECTS_STOPPING_CROSSSECTION_N_PAR + i + 3] # not used at the moment
        self.index = index

        if self.include_target_integration:
            self.tt = TargetThickness(self.index)
        else:
            self.tt = None
        

    def string(self):
        row = self.row.copy()
        row[EFFECT_INCLUDE_INDEX] = '1' if self.include else '0'
        row[EFFECTS_INTEGRATION_POINTS] = str(self.integration_points)
        row[EFFECTS_INCLUDE_GAUSSIAN_CONVOLUTION] = '1' if self.include_gaussian_convolution else '0'
        row[EFFECTS_GAUSSIAN_CONVOLUTION_SIGMA] = str(self.gaussian_convolution_sigma)
        row[EFFECTS_INCLUDE_TARGET_INTEGRATION] = '1' if self.include_target_integration else '0'
        row[EFFECTS_TARGET_THICKNESS] = str(self.target_thickness)
        row[EFFECTS_STOPPING_CROSSSECTION_N_PAR] = str(self.stopping_crosssection_n_par)
        for i in range(self.stopping_crosssection_n_par):
            row[EFFECTS_STOPPING_CROSSSECTION_N_PAR + i + 1] = str(self.stopping_crosssection_par[i])
        row[EFFECTS_STOPPING_CROSSSECTION_N_PAR + i + 2] = '1' if self.include_att_coeffs else '0'
        row[EFFECTS_STOPPING_CROSSSECTION_N_PAR + i + 3] = str(self.att_coeffs)
        return ' '.join(row)

class EffectsList:
    def __init__(self, filename) -> None:
        self.contents = utility.read_input_file(filename)
        i = self.contents.index('<targetInt>')+1
        j = self.contents.index('</targetInt>')

        self.effects = [] # list of Effect objects

        k = 0
        for row in self.contents[i:j]:
            if row != '':
                row_list = row.split()
                if int(row_list[EFFECT_INCLUDE_INDEX]) == 1:
                    self.effects.append(Effect(row, k))
                k += 1

        # list of indexes of effects with target integration, 
        # it's needed manly for the label property of the Config class
        self.target_int_indexes = [] 
        for (i, eff) in enumerate(self.effects):
            if eff.include and eff.include_target_integration:
                self.target_int_indexes.append(i)

    def write_effects(self, contents):
        start = contents.index('<targetInt>')+1
        #stop = contents.index('</targetInt>')

        for effect in self.effects:
            contents[start + effect.index] = effect.string()
        
        return contents
    
    def update_target_thickness(self, theta_target_thickness, contents):
        assert len(theta_target_thickness) == len(self.target_int_indexes), 'Number of target thickness parameters does not match number of target thickness effects.'

        for (f, i) in zip(theta_target_thickness, self.target_int_indexes):
            self.effects[i].target_thickness = f

        self.write_effects(contents)
        
        return contents 
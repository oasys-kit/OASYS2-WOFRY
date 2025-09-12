from wofryimpl.beamline.beamline import WOBeamline
from wofry.propagator.wavefront import Wavefront

class WofryData(object):
    def __init__(self, beamline=None, wavefront=None):
        super().__init__()
        if beamline is None:
            self.__beamline = WOBeamline()
        else:
            self.__beamline = beamline

        if wavefront is None:
            self.__wavefront = Wavefront()
        else:
            self.__wavefront = wavefront

    def get_beamline(self):
        return self.__beamline

    def get_wavefront(self):
        return self.__wavefront

    def set_beamline(self, beamline):
        self.__beamline = beamline.duplicate()

    def set_wavefront(self, wavefront):
        self.__wavefront = wavefront.duplicate()

    def duplicate(self):
        return WofryData(wavefront=self.get_wavefront().duplicate(),
                         beamline=self.get_beamline().duplicate())



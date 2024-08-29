from devices_control import *

class Spectramaker:


    def __init__(self):
        self.motor: Motor = Motor()
        self.wavemeter : Wavemeter = Wavemeter()
        self.energymeter: Energiser = Energiser()
        self.oscilloscope: Oscilloscope = Oscilloscope()

    # def calibrate(self) -> None:
    #     file_wavelength = open('file_wavelength.txt', 'w')
    #     file_energy = open('file_energy.txt', 'w')
    #     self.motor.go_home_both(1)
    #     self.motor.go_relative(1,69280)
    #     # self.motor.go_relative(2, 87960)
    #     time.sleep(5)
    #     wavelength = self.wavemeter.get_wavelength()
    #     self.energymeter.set_wavelength(wavelength / 2)
    #     self.energymeter.refresh()
    #     # self.go_until(1, target_wavelength=self.min_wavelength, step=self.step)
    #     sh_energy = self.energymeter.get_average_energy(10)
    #     while self.wavemeter.get_wavelength() < self.max_wavelength:
    #         self.energymeter.refresh()
    #         wavelength = self.wavemeter.get_wavelength()
    #         self.energymeter.set_wavelength(wavelength / 2)
    #         time.sleep(2)
    #         sh_energy = self.energymeter.get_average_energy(5)
    #         while sh_energy < 10**-4:
    #             self.motor.go_relative(2, 30)
    #             sh_energy = self.energymeter.get_average_energy(5)
    #             print(sh_energy)
    #         energy_down = 0
    #         while True:
    #             old_energy = sh_energy
    #             self.motor.go_relative(2, 10)
    #             print(self.motor.get_position(2))
    #             sh_energy = self.energymeter.get_average_energy(10)
    #             print(sh_energy)
    #             if sh_energy < old_energy:
    #                 if energy_down == 1:
    #                     self.motor.go_relative(2, -2000)
    #                     self.motor.go_relative(2, 1980)
    #                     self.save_parameters(file_wavelength, file_energy)
    #                     break # end of iteration
    #                 else:
    #                     energy_down = 1
    #             else:
    #                 energy_down = 0
    #         self.motor.go_relative(1, self.step)
    #         print('нексиль')
    #     file_wavelength.close()
    #     file_energy.close()

    def save_parameters(self, file_wavelength: str, file_energy: str) -> None:
        self.energymeter.refresh()
        time.sleep(1)
        print('saving energy ', self.energymeter.get_average_energy(10))
        wavelength = str(self.wavemeter.get_wavelength()).replace('.', ',')[0:7]
        file_wavelength.write(f'{self.motor.get_position(1)}/{wavelength}/{self.motor.get_position(2)}/1\n')
        file_energy.write(f'{wavelength}\t{self.energymeter.get_average_energy(20)}\n')

    def go_until(self, id: int, target_wavelength: float, step: int = 10) -> None:
        current_wavelength = 400
        if current_wavelength > target_wavelength:
            direction = -1
        else:
            direction = 1
        difference = direction * (target_wavelength - current_wavelength)
        while difference > 0:
            if difference > 2:
                self.motor.go_relative(id, direction*700)
            elif difference > 0.2:
                self.motor.go_relative(id, direction*100)
            else:
                self.motor.go_relative(id, direction*15)
            self.motor.wait_for_free(1)
            time.sleep(0.2)
            self.motor.get_position(2)
            print(self.wavemeter.get_wavelength())
            current_wavelength = self.wavemeter.get_wavelength()
            difference = direction * (target_wavelength - current_wavelength)

    def inspect_energy(self) -> None:
        wavelength = []
        motor_1 = []
        motor_2 = []
        energy = []
        # self.motor.go_home_both()
        file_res = open(r'sh_energy_dependence.txt', 'a')
        with open(r'general_calibration.txt', 'r') as file:
            for line in file:
                wavelength += [float(line.strip().split()[0])]
                motor_1 += [int(line.strip().split()[1])]
                motor_2 += [int(line.strip().split()[2])]
        for i in range(len(motor_1)):
            if wavelength[i] < 635.160:
                continue
            if wavelength[i] == 635.160:
                while input('Поменяйте положение зеркала и напечатайте \'next\': ') != 'next':
                    continue
            self.motor.go_absolute(1, motor_1[i])
            self.motor.go_absolute(2, motor_2[i])
            self.energymeter.set_wavelength(wavelength[i])
            self.energymeter.refresh()
            time.sleep(2.5)
            energy = self.energymeter.get_average_energy(20) * 1000
            print('wavelength = ', wavelength[i], '\t energy = ', energy)
            file_res.write(f'{wavelength[i]}\t{energy}\n')
        file_res.close()

    def get_spectrum(self, wavelength_min: float, wavelength_max: float, average_count: int = 100,\
                      wavelength_step: float = 0., folder: str = "data") -> None:
        if (os.path.isdir(folder)):
            pass
        else:
            os.mkdir(folder)
        self.oscilloscope.set_acquire_average_mode()
        self.oscilloscope.set_acquire_count(average_count)
        self.motor.go_home(1)
        self.motor.go_home(2)
        count = self.oscilloscope.get_acquire_count()
        file = open(f'full_calibration.txt', 'r')
        file_cal = open(f'{folder}\\calibration_file.txt', 'w')
        for line in file:
            wave = line.strip().split('\t')[0].replace(',', '.')
            motor_1 = int(line.strip().split('\t')[1])
            motor_2 = int(line.strip().split('\t')[2])
            if float(wave) < wavelength_min:
                continue
            if float(wave) > wavelength_max:
                continue
            self.motor.go_absolute(1, motor_1)
            self.motor.go_absolute(2, motor_2)
            time.sleep(1)
            wavelength = wave
            self.oscilloscope.run_acquision()
            time.sleep(count / 10. + 1.5) # частота лазера, обычно 10 Гц
            self.oscilloscope.save_file(f'{folder}\\{str(wavelength)[:7]}.txt')
            file_cal.write(f'{str(wavelength)[:7]}\t{motor_1}\t{motor_2}\n')
            print('got on ', wavelength)
            wavelength = float((int(float(wavelength) * 1000) + int(wavelength_step * 1000)) / 1000)
            wavelength_min = wavelength
        file.close()
        file_cal.close()

    def get_nopump_signal(self) -> None:
        self.oscilloscope.set_acquire_average_mode()
        self.oscilloscope.set_acquire_count(200)
        count = self.oscilloscope.get_acquire_count()
        self.oscilloscope.run_acquision()
        time.sleep(count / 10 + 1.5)
        self.oscilloscope.save_file(f'spectrum_5\\only_dye_312.15_end_1.35mJ.txt')

    def get_energy_profile(self, n) -> None:
        file_1 = open(f'spectrum_5\\energy_profile.txt', 'w')
        file = open('spectrum_5\\calibration_file.txt', 'r')
        self.motor.go_home(1)
        self.motor.go_home(2)
        for line in file:
            wave = line.strip().split('\t')[0].replace(',', '.')
            motor_1 = int(line.strip().split('\t')[1])
            motor_2 = int(line.strip().split('\t')[2])
            # if float(wave) < 588.63:
            #     continue
            # if float(wave) > 599.251:
            #     continue
            self.motor.go_absolute(1, motor_1)
            self.motor.go_absolute(2, motor_2)
            self.energymeter.refresh()
            time.sleep(1)
            wavelength = self.wavemeter.get_wavelength()
            self.energymeter.set_wavelength(wavelength / 2)
            energy = self.energymeter.get_average_energy(30)
            file_1.write(f'{wavelength}\t{energy * 1000}\n')

        file.close()
        file_1.close()

    def go_wavelength(self, wavelength_goal: str) -> None:
        file = open("full_calibration.txt", 'r')
        for line in file:
            wavelength = float(line.strip().split('\t')[0].replace(',', '.'))
            if (wavelength == wavelength_goal):
                motor_1 = int(line.strip().split('\t')[1])
                motor_2 = int(line.strip().split('\t')[2])
                self.motor.go_absolute(1, motor_1)
                self.motor.go_absolute(2, motor_2)


    





                

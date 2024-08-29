from spectramaker import *
Design, _ = uic.loadUiType('gui_window.ui')
class MainWindow(QMainWindow, Design):
    def __init__(self):
        self.sm = Spectramaker()
        super().__init__()
        #явно объявляю виджеты из .ui файла
        self.setupUi(self)
        self.wavemeterConnectButton: QPushButton = self.wavemeterConnectButton
        self.energymeterConnectButton: QPushButton= self.energymeterConnectButton 
        self.motorConnectButton: QPushButton = self.motorConnectButton
        self.oscilloscopeConnectButton: QPushButton = self.oscilloscopeConnectButton
        self.getEnergyProfilePushButton: QPushButton = self.getEnergyProfilePushButton
        self.getSpectrumPushButton: QPushButton = self.getSpectrumPushButton
        self.warningWindowLineEdit: QtWidgets.QLineEdit = self.warningWindowLineEdit
        self.wavelengthStartSpinBox: QtWidgets.QDoubleSpinBox = self.wavelengthStartSpinBox
        self.wavelengthEndSpinBox: QtWidgets.QDoubleSpinBox = self.wavelengthEndSpinBox
        self.filenameLineEdit: QtWidgets.QLineEdit = self.filenameLineEdit
        self.folderLineEdit: QtWidgets.QLineEdit = self.folderLineEdit
        self.refreshRateSpinBox: QtWidgets.QSpinBox = self.refreshRateSpinBox
        self.wavelengthStepSpinBox: QtWidgets.QDoubleSpinBox = self.wavelengthStepSpinBox
        self.goHomeButton: QPushButton = self.goHomeButton
        self.wavemeterWavelengthLineEdit: QtWidgets.QLineEdit = self.wavemeterWavelengthLineEdit
        self.calibrationWavelengthLineEdit: QtWidgets.QLineEdit = self.calibrationWavelengthLineEdit
        self.recalibrateButton: QPushButton = self.recalibrateButton
        self.goToSpinBox: QtWidgets.QDoubleSpinBox = self.goToSpinBox
        self.goToPushButton: QPushButton = self.goToPushButton
        self.averageCountSpinBox: QtWidgets.QSpinBox = self.averageCountSpinBox

        self.setWindowTitle("Autospectromizer")
        self.show_warning_message('no messages')
        self.pushButton.clicked.connect(self.real_talk)
        self.wavemeterConnectButton.setStyleSheet("background-color: red;")
        self.energymeterConnectButton.setStyleSheet("background-color: red;")
        self.motorConnectButton.setStyleSheet("background-color: red;")
        self.oscilloscopeConnectButton.setStyleSheet("background-color: red;")
        self.wavemeterConnectButton.clicked.connect(self.wavemeter_connect)
        self.refreshRateSpinBox.valueChanged.connect(self.change_refresh_rate)
        self.energymeterConnectButton.clicked.connect(self.energymeter_connect)
        self.wavemeterConnectButton.clicked.connect(self.wavemeter_connect)
        self.motorConnectButton.clicked.connect(self.motor_connect)
        self.oscilloscopeConnectButton.clicked.connect(self.oscilloscope_connect)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_global)
        self.setMinimumSize(915,600)
        self.setMaximumSize(1800,800)
        self.timer.start(1000)
        self.refreshRateSpinBox.setValue(self.timer.interval())
        self.goHomeButton.clicked.connect(self.go_home_motors)
        self.goToPushButton.clicked.connect(self.goto_wavelength)
        self.recalibrateButton.clicked.connect(self.recalibrate)
        self.getSpectrumPushButton.clicked.connect(self.get_spectrum)

        self.spinboxes_limits_init()

    def update_global(self) -> None:
        self.pushButton.setText("random button")
        n = random.random()
        if n < 0.33:
            self.pushButton.setStyleSheet("background-color: green;")
        elif n > 0.66:
            self.pushButton.setStyleSheet("background-color: yellow;")
        else:
            self.pushButton.setStyleSheet("background-color: blue;")
        
        if self.sm.wavemeter.is_connected:
            self.wavemeterWavelengthLineEdit.setText(str(self.sm.wavemeter.get_wavelength(force=True))[0:7])
        if self.sm.motor.is_connected:
            self.calibrationWavelengthLineEdit.setText(self.translate_to_wavelength(self.sm.motor.get_position(1)))

    def real_talk(self) -> None:
        self.pushButton.setText("clicked")

    @pyqtSlot()
    def change_refresh_rate(self) -> None:
        self.timer.setInterval(self.refreshRateSpinBox.value())

    @pyqtSlot()
    def energymeter_connect(self) -> None:
        for i in range(3, 10):
            try:
                self.sm.energymeter.connect(i)
                self.energymeterConnectButton.setStyleSheet("background-color: green;")
                self.warningWindowLineEdit.setText('energymeter connected!')
                self.sm.energymeter.is_connected = True
                break
            except:
                self.warningWindowLineEdit.setText(f'energymeter not connected at COM{i}')
                self.energymeterConnectButton.setStyleSheet("background-color: red;")


    
    @pyqtSlot()
    def wavemeter_connect(self) -> None:
        with contextlib.suppress(OSError):
            try:
                self.sm.wavemeter.connect() 
                self.wavemeterConnectButton.setStyleSheet("background-color: green;")
                self.warningWindowLineEdit.setText('wavemeter connected!')
                self.sm.wavemeter.is_connected = True
            except:
                self.wavemeterConnectButton.setStyleSheet("background-color: red;")
                self.warningWindowLineEdit.setText('wavemeter not connected!')

    @pyqtSlot()
    def motor_connect(self) -> None:
        try:
            self.sm.motor.connect()
            self.motorConnectButton.setStyleSheet("background-color: green;")
            self.warningWindowLineEdit.setText('motor connected!')
            self.sm.motor.is_connected = True
        except:
            self.warningWindowLineEdit.setText(f'motor not connected')
            self.motorConnectButton.setStyleSheet("background-color: red;")

    @pyqtSlot()
    def oscilloscope_connect(self) -> None:
        try:
            self.sm.oscilloscope.connect()
            self.oscilloscopeConnectButton.setStyleSheet("background-color: green;")
            self.warningWindowLineEdit.setText('oscilloscope connected!')
            self.sm.oscilloscope.is_connected = True
        except:
            self.warningWindowLineEdit.setText(f'oscilloscope not connected')
            self.oscilloscopeConnectButton.setStyleSheet("background-color: red;")

    @pyqtSlot()
    def show_warning_message(self, message: str) -> None:
        self.warningWindowLineEdit.setText(message)
        self.warningWindowLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

    @pyqtSlot()
    def go_home_motors(self) -> None:
        if self.sm.motor.is_connected:
            self.update()
            self.sm.motor.go_home(1)
            self.sm.motor.go_home(2)
            self.warningWindowLineEdit.setText('Motors are homed!')
            self.goHomeButton.setStyleSheet("background-color: green;")
        else:
            self.goHomeButton.setStyleSheet("background-color: red;")

    def translate_to_wavelength(self, x: int) -> str:
        file = open("full_calibration.txt", 'r')
        for line in file:
            motor_1 = int(line.strip().split('\t')[1])
            if motor_1 == x:
                file.close()
                return (line.strip().split('\t')[0].replace(',', '.'))
        file.close()
        return "no calibration here"
    
    def spinboxes_limits_init(self) -> None:
        file = open("full_calibration.txt", 'r')
        k = 0
        for line in file:
            wavelength = (line.strip().split('\t')[0].replace(',', '.'))[:7]
            if k == 0:
                self.goToSpinBox.setMinimum(float(wavelength))
                self.wavelengthStartSpinBox.setMinimum(float(wavelength))
                self.wavelengthEndSpinBox.setMinimum(float(wavelength))
                k+=1
        self.goToSpinBox.setMaximum(float(wavelength))
        self.wavelengthStartSpinBox.setMaximum(float(wavelength))
        self.wavelengthEndSpinBox.setMaximum(float(wavelength))
        file.close()

    @pyqtSlot()
    def goto_wavelength(self) -> None:
        if self.sm.motor.is_connected == False:
            pass
        else:
            print("here")
            new_wavelength = self.goToSpinBox.value()
            file = open("full_calibration.txt", 'r')
            for line in file:
                wavelength = (line.strip().split('\t')[0].replace(',', '.'))[:7]
                if (float(new_wavelength) == float(wavelength)):
                    motor_1 = int(line.strip().split('\t')[1])
                    motor_2 = int(line.strip().split('\t')[2])
                    self.sm.motor.go_absolute(1, motor_1)
                    self.sm.motor.go_absolute(2, motor_2)
                    break
            file.close()

    @pyqtSlot()
    def recalibrate(self) -> None:
        if self.sm.wavemeter.is_connected and self.sm.motor.is_connected:
            real_wavelength = self.wavemeterWavelengthLineEdit.text()
            cal_wavelength = self.calibrationWavelengthLineEdit.text()
            if (real_wavelength in ['under', 'over'] or cal_wavelength == 'no calibration here'):
                return
            else:
                real_wavelength = int(float(real_wavelength) * 1000)
                cal_wavelength = int(float(cal_wavelength) * 1000)
                diff = real_wavelength - cal_wavelength
                file = open("full_calibration.txt", 'r')
                new_file = open("temp_calibration.txt", 'w')
                for line in file:
                    wavelength = (int(float((line.strip().split('\t')[0].replace(',', '.'))[:7]) * 1000) + diff) / 1000
                    motor_1 = int(line.strip().split('\t')[1])
                    motor_2 = int(line.strip().split('\t')[2])
                    new_file.write(f"{str(wavelength)[:7]}\t{motor_1}\t{motor_2}\n")
                file.close()
                new_file.close()
                os.remove('full_calibration.txt')
                os.rename('temp_calibration.txt', 'full_calibration.txt')
                self.spinboxes_limits_init()

    @pyqtSlot()
    def get_spectrum(self) -> None:   #в названии файлов используется длина волны из калибровки!!! так быстрее и проще)
        if self.sm.motor.is_connected == False:
            self.warningWindowLineEdit.setText("Motor is not connected!")
            return
        if self.sm.oscilloscope.is_connected == False:
            self.warningWindowLineEdit.setText("Oscilloscope is not connected!")
            return
        if self.filenameLineEdit.text() == "":
            self.warningWindowLineEdit.setText("Empty filename!")
            return
        folder = self.folderLineEdit.text()
        average_count = self.averageCountSpinBox.value()
        wavelength_step = self.wavelengthStepSpinBox.value()
        wavelength_min = self.wavelengthStartSpinBox.value()
        wavelength_max = self.wavelengthEndSpinBox.value()
        self.sm.get_spectrum(wavelength_min=wavelength_min, wavelength_max=wavelength_max,average_count=average_count,\
                             wavelength_step=wavelength_step, folder=folder)
        self.warningWindowLineEdit.setText("The experiment has ended!")
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    window = MainWindow()
    window.show()
    app.exec()
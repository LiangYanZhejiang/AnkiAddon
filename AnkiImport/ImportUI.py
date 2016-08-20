from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(648, 413)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_4 = QtGui.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_6.addWidget(self.label_4)
        self.ImportDir = QtGui.QLineEdit(Form)
        self.ImportDir.setEnabled(False)
        #self.ImportDir.setMouseTracking(True)
        self.ImportDir.setObjectName("ImportDir")
        self.horizontalLayout_6.addWidget(self.ImportDir)
        spacerItem = QtGui.QSpacerItem(75, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_5.addWidget(self.label_3)
        self.WordlistFile = QtGui.QLineEdit(Form)
        self.WordlistFile.setEnabled(True)
        self.WordlistFile.setObjectName("WordlistFile")
        self.horizontalLayout_5.addWidget(self.WordlistFile)
        self.browse = QtGui.QPushButton(Form)
        self.browse.setObjectName("browse")
        self.horizontalLayout_5.addWidget(self.browse)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QtGui.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.DecksName = QtGui.QLineEdit(Form)
        self.DecksName.setEnabled(True)
        self.DecksName.setObjectName("DecksName")
        self.horizontalLayout_4.addWidget(self.DecksName)
        spacerItem1 = QtGui.QSpacerItem(250, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        spacerItem2 = QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem2)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 1, 1, 1)
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.FrontEdit = QtGui.QTextEdit(Form)
        self.FrontEdit.setObjectName("FrontEdit")
        self.gridLayout_3.addWidget(self.FrontEdit, 1, 0, 1, 1)
        self.BackEdit = QtGui.QTextEdit(Form)
        self.BackEdit.setObjectName("BackEdit")
        self.gridLayout_3.addWidget(self.BackEdit, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Form)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_3.addWidget(self.buttonBox, 2, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Words Import",None))
        self.label_4.setText(_translate("Form", "Import directory:",None))
        self.label_3.setText(_translate("Form", " Words List Path:",None))
        self.browse.setText(_translate("Form", "Browse",None))
        self.label_5.setText(_translate("Form", "      Decks Name:",None))
        self.label_2.setText(_translate("Form", "Back:",None))
        self.label.setText(_translate("Form", "Front:",None))


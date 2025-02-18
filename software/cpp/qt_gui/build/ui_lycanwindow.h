/********************************************************************************
** Form generated from reading UI file 'lycanwindow.ui'
**
** Created by: Qt User Interface Compiler version 6.8.2
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_LYCANWINDOW_H
#define UI_LYCANWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_LycanWindow
{
public:
    QWidget *centralwidget;
    QMenuBar *menubar;
    QStatusBar *statusbar;

    void setupUi(QMainWindow *LycanWindow)
    {
        if (LycanWindow->objectName().isEmpty())
            LycanWindow->setObjectName("LycanWindow");
        LycanWindow->resize(800, 600);
        centralwidget = new QWidget(LycanWindow);
        centralwidget->setObjectName("centralwidget");
        LycanWindow->setCentralWidget(centralwidget);
        menubar = new QMenuBar(LycanWindow);
        menubar->setObjectName("menubar");
        menubar->setGeometry(QRect(0, 0, 800, 22));
        LycanWindow->setMenuBar(menubar);
        statusbar = new QStatusBar(LycanWindow);
        statusbar->setObjectName("statusbar");
        LycanWindow->setStatusBar(statusbar);

        retranslateUi(LycanWindow);

        QMetaObject::connectSlotsByName(LycanWindow);
    } // setupUi

    void retranslateUi(QMainWindow *LycanWindow)
    {
        LycanWindow->setWindowTitle(QCoreApplication::translate("LycanWindow", "LycanWindow", nullptr));
    } // retranslateUi

};

namespace Ui {
    class LycanWindow: public Ui_LycanWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_LYCANWINDOW_H

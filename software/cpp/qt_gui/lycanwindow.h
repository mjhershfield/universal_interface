#ifndef LYCANWINDOW_H
#define LYCANWINDOW_H

#include <QTabWidget>
#include "peripheralTab.h"

QT_BEGIN_NAMESPACE
namespace Ui {
class LycanWindow;
}
QT_END_NAMESPACE

class LycanWindow : public QTabWidget
{
    Q_OBJECT

public:
    LycanWindow(Lycan* dev, std::mutex* mut, QWidget *parent = nullptr);
    ~LycanWindow();

private:
    Ui::LycanWindow *ui;
};
#endif // LYCANWINDOW_H

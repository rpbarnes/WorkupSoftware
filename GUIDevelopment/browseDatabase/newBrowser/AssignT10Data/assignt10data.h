#ifndef ASSIGNT10DATA_H
#define ASSIGNT10DATA_H

#include <QDialog>

namespace Ui {
class assignT10Data;
}

class assignT10Data : public QDialog
{
    Q_OBJECT

public:
    explicit assignT10Data(QWidget *parent = 0);
    ~assignT10Data();

private:
    Ui::assignT10Data *ui;
};

#endif // ASSIGNT10DATA_H

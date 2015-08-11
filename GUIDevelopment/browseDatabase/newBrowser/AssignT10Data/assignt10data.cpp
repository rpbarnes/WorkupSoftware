#include "assignt10data.h"
#include "ui_assignt10data.h"

assignT10Data::assignT10Data(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::assignT10Data)
{
    ui->setupUi(this);
}

assignT10Data::~assignT10Data()
{
    delete ui;
}

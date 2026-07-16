# =========================================================
# PALETA CLARA MODERNA
# =========================================================

STYLE = """
QMainWindow {
    background-color: #eef2f7;
}

QWidget {
    background-color: #eef2f7;
    color: #2d3748;
    font-size: 14px;
    font-family: "Segoe UI";
}

/* ======================================================
   SIDEBAR
====================================================== */

QFrame#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #d9e1ea;
}

/* TÍTULO */
QLabel#title {
    font-size: 24px;
    font-weight: 700;
    color: black;
    background-color: white;
    padding: 14px;
    border-radius: 14px;
}

/* MENU */
QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
}

/* REMOVE SCROLLBAR */
QScrollBar:vertical,
QScrollBar:horizontal {
    width: 0px;
    height: 0px;
    background: transparent;
}

QListWidget::item {
    padding: 14px;
    margin: 5px 6px;
    border-radius: 14px;

    color: #4b5563;
    font-size: 15px;
}

QListWidget::item:hover {
    background-color: #edf4ff;
    color: #2563eb;
}

QListWidget::item:selected {
    background-color: #dbeafe;
    color: #1d4ed8;
    font-weight: 600;
}

/* ======================================================
   CONTEÚDO
====================================================== */

QLabel#pageTitle {
    font-size: 30px;
    font-weight: 700;
    color: #111827;
}

QLabel#fieldLabel {
    font-size: 13px;
    font-weight: 600;
    color: #374151;
    margin-top: 4px;
}

QLabel#displayCronometro {
    font-size: 45px;
    font-weight: 600;
    color: #111827;
}

QPushButton {
    background-color: white;
    
    border: 1px solid #d6dee8;
    border-radius: 16px;

    padding-top: 10px;
    padding-right: 16px;
    padding-bottom: 10px;
    padding-left: 16px;

    font-size: 15px;
    font-weight: 400;

    color: #374151;
}

QPushButton#kanban {
    background-color: white;
    
    border: 1px solid #d6dee8;
    border-radius: 16px;

    padding-top: 0px;
    padding-right: 12px;
    padding-bottom: 0px;
    padding-left: 12px;

    font-size: 15px;
    font-weight: 200;

    color: #374151;
}

QPushButton:hover {
    background-color: #f8fbff;
    border: 1px solid #bfdbfe;
    color: #2563eb;
}

QPushButton:pressed {
    background-color: #e8f0ff;
}

/* ======================================================
   DISCIPLINAS
====================================================== */

QTreeWidget {
    background-color: white;

    border: 1px solid #d9e1ea;
    border-radius: 16px;

    padding: 8px;

    outline: none;
}

/* ======================================================
   CALENDÁRIO - LINHA DE DATA
====================================================== */

QDateEdit {
    background-color: white;
    border: 1px solid #d9e1ea;
    border-radius: 12px;
    padding: 8px 12px;
    min-height: 22px;
    color: #374151;
    font-size: 14px;
}

QDateEdit:hover {
    border: 1px solid #2563eb;
}

QDateEdit:focus {
    border: 2px solid #2563eb;
}

/* Botão do calendário */
QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;

    width: 32px;

    border-left: 1px solid #d9e1ea;
    background-color: transparent;

    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
}

/* Hover do botão */
QDateEdit::drop-down:hover {
    background-color: #edf4ff;
}

/* ======================================================
   CALENDÁRIO - WIDGET
====================================================== */

QCalendarWidget {
    background-color: white;
    border: 1px solid #d9e1ea;
    border-radius: 18px;
    padding: 12px;
}

QCalendarWidget QWidget {
    background-color: white;
}

/* Cabeçalho mês/ano */
QCalendarWidget QToolButton {
    background-color: transparent;
    color: #374151;
    font-size: 15px;
    font-weight: 600;
    border: none;
    border-radius: 10px;
    padding: 8px;
}

QCalendarWidget QToolButton:hover {
    background-color: #edf4ff;
    color: #2563eb;
}

/* Menu mês/ano */
QCalendarWidget QMenu {
    background-color: white;
    border: 1px solid #d9e1ea;
}

QCalendarWidget QMenu::item:selected {
    background-color: #dbeafe;
}

/* Barra superior */
QCalendarWidget QSpinBox {
    background-color: white;
    border: 1px solid #d9e1ea;
    border-radius: 10px;
    padding: 4px;
}

/* Dias da semana */
QCalendarWidget QTableView {
    selection-background-color: #2563eb;
    selection-color: white;

    outline: none;

    border: none;

    alternate-background-color: #f8fafc;

    color: #374151;

    font-size: 14px;
}

QCalendarWidget QTableView::item:hover {
    background-color: #93c5fd;
    border-radius: 8px;
}

/* Cabeçalho Seg Ter Qua... */
QCalendarWidget QHeaderView::section {
    background-color: #f8fafc;
    color: #374151;
    border: none;
    padding: 8px;
    font-weight: 600;
}

"""
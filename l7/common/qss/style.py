# ====={ ROOT }=====
COMMON_THEME = '''
    background-color: rgb(33,37,43);
    color: rgb(171,178,191);
'''

MENU_BAR_THEME = '''
    
    QMenuBar {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 rgb(27,31,37), stop:1 rgb(33,37,43));
        color: rgb(171,178,191);
        spacing: 3px;
        
    }
    
    QMenuBar::item {
        margin: 2px 0;
        padding: 1px 15px 1px 5px;
        background-color: transparent;
        border-radius: 5px;
    }
    
    QMenuBar::item:selected { 
        background-color: rgb(40,44,52);
    }
    
    QMenuBar::item:pressed {
        background-color: rgb(53,115,212);
        color: rgb(27,31,37);
    }
'''

TABLE_THEME = '''
    QAbstractItemView {
        background-color: transparent;
        border-radius: 6px;
    }
    
    QTableCornerButton::section {
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0.7, y2: 0.7,
                                            stop: 0 rgb(40,44,52), stop: 0.9 rgb(33,37,43));
        border-top-left-radius: 6px;
    }                                        
    
    QHeaderView::section {
        border-style: none;
        border: 1px solid transparent;
        background-color: rgb(33,37,43);
    }
    
    QHeaderView::section:hover, QHeaderView::section:pressed {
        color: rgb(53,115,212);
        background-color: rgb(40,44,52);
    }
    
    QHeaderView::section:horizontal:last {
        border-style: none;
        border-top-right-radius: 6px;                                            
        /*border-bottom-right-radius: 6px;*/
    }
    
    QHeaderView::section:vertical:last {
        border-style: none;
        border-bottom-left-radius: 6px;
        /*border-bottom-right-radius: 6px;*/
    }
        
    QHeaderView::section:horizontal:hover {
        border-bottom: 1px solid rgb(53,115,212);
    }
    QHeaderView::section:vertical:hover {
        border-right: 1px solid rgb(53,115,212);
    }
    
    QTableView {
        outline:none;
        margin: 1px;
        color: rgb(171,178,191);
        background-color: rgb(27,31,37);
        border-radius: 6px;
        selection-background-color: transparent;
    }
    
    QTableView::item {
        margin: 1px;
        color: rgb(171,178,191);
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0.7, y2: 0.7,
                                            stop: 0 rgb(40,44,52), stop: 0.9 rgb(33,37,43));
        border: 1px solid transparent;
        border-radius: 6px;
    }
    
    QTableView::item:hover {
        margin: 1px;
        border: 1px solid rgb(53,115,212);
        border-radius: 6px;
    }
    
    QTableView::item:selected {
        margin: 1px;
        color: rgb(27,31,37);
        background-color: rgb(53,115,212);
        border: 1px solid rgb(53,115,212);
        border-radius: 6px;
    }
'''

# ====={ ELEMENTS }=====
HIDDEN_LABEL_THEME = '''
    QLabel {
        font-size: 13px;
        color: rgb(255,100,100);
    }        
'''

NEW_MESSAGE_LABEL_THEME = '''
    QLabel {
        border-radius: 15px;
        background-color: rgba(27,31,37,100);
    }
'''

INPUT_NAME_THEME = '''
    QLineEdit {
        border: 1px solid rgba(171,178,191,150);
        border-radius: 5px;
    }
    QLineEdit:focus { 
        border: 1px solid rgb(53,115,212);
        background-color: rgb(27,31,37); 
    }
    QLineEdit:hover { 
        background-color: rgb(40,44,52); 
    }
'''

DISABLED_INPUT_NAME_THEME = '''
    QLineEdit {
        border: 1px solid rgba(171,178,191,150);
        border-radius: 5px;
        padding: 0 37px 0 8px;
    }
    QLineEdit:focus { 
        border: 1px solid rgb(53,115,212);
        background-color: rgb(27,31,37); 
    }
'''

CONTACTS_THEME = '''
    QListView { 
        outline: none;
        background-color: rgb(27,31,37); 
        padding: 5px 5px 35px 5px; 
        border-radius: 6px;
        border: 1px solid rgb(27,31,37);
    }
    QListView::item {
        margin: 1px 0;
        padding: 1px 4px;
        background-color: transparent;
        border-radius: 4px;
        border: 1px solid transparent;
    }
    QListView::item:hover {
        border: 1px solid rgb(53,115,212);        
    }
    QListView::item:selected {
        border: 1px solid rgb(53,115,212);        
        background-color: rgb(53,115,212);
        color: rgb(27,31,37);
    }
'''

MESSAGES_HIST_THEME = '''
    QListView { 
        outline: none;
        /*background-color: rgb(27,31,37);*/ 
        padding: 5px 5px 55px 5px; 
        border-radius: 6px;
        border: 1px solid rgb(27,31,37);
        background: url(common/img/img.jpg)
        
    }
'''

MESSAGE_THEME = '''
    QTextEdit:!hover { 
        padding: 0 95px 0 0; 
        border-bottom-left-radius: 6px;
        border-bottom-right-radius: 6px;
        border: 1px solid rgb(27,31,37);
    }
    QTextEdit:hover { 
        background-color: rgb(40,44,52); 
        padding: 0 35px 0 0; 
        border-bottom-left-radius: 6px;
        border-bottom-right-radius: 6px;
        border: 1px solid rgb(27,31,37);
    }
    QTextEdit:focus { 
        background-color: rgb(27,31,37); 
        padding: 0 35px 0 0;
        border-bottom-left-radius: 6px;
        border-bottom-right-radius: 6px;
        border: 1px solid rgb(27,31,37);
    }
'''

COMBOBOX_THEME = '''
    QComboBox:!hover {
        background-color: rgb(40,44,52); 
        border-radius: 6px;
    }
    QComboBox:focus { 
        background-color: rgb(27,31,37); 
        border-radius: 6px;
    }
    QComboBox:hover { 
        background-color: rgb(40,44,52); 
        border-radius: 6px;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
    
        border-left-width: 1px;
        border-left-color: rgb(40,44,52);
        border-left-style: solid;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
    }
    QComboBox::down-arrow {
        image: url(common/img/arrow_down);
        width: 20px;
        height: 20px;
    }
    QComboBox::down-arrow:on {
        image: url(common/img/arrow_up);
        width: 20px;
        height: 20px;
    }
    QComboBox::item {
        max-height: 25px;
        border: 1px solid transparent;
        border-radius: 6px;
    }
    QComboBox::item:selected {
        max-height: 25px;
        background: rgb(27,31,37);
        border-radius: 6px;
    }
    QComboBox QAbstractItemView {
        border: 1px solid rgb(53,115,212);
        /*border-radius: 6px;*/
        padding: 3px;
    }
'''

# ====={ BUTTONS }=====
OK_BTN_THEME = '''
    QPushButton:!hover { 
        background-color: rgb(53,115,212); 
        color: rgb(27,31,37);
        border-radius: 6px;
    }
    QPushButton:hover { 
        background-color: rgb(73,135,232); 
        color: rgb(27,31,37);
        border-radius: 6px;
    }
'''

EXIT_BTN_THEME = '''
    QPushButton:!hover { 
        background-color: rgb(27,31,37); 
        border: 1px solid rgb(206,95,82);
        border-radius: 6px;
    }
    QPushButton:hover { 
        background-color: rgb(206,95,82); 
        color: rgb(27,31,37);
        border: 1px solid rgb(206,95,82);
        border-radius: 6px;
    }
'''

DEL_BTN_THEME = '''
    QPushButton:!hover { 
        background-color: rgb(206,95,82); 
        color: rgb(27,31,37);
        border-radius: 6px;
    }
    QPushButton:hover { 
        background-color: rgb(226,115,102); 
        color: rgb(27,31,37);
        border-radius: 6px;
    }
'''

CANCEL_BTN_THEME = '''
    QPushButton:!hover { 
        background-color: rgb(27,31,37); 
        border-radius: 6px;
    }
    QPushButton:hover { 
        background-color: rgb(40,44,52); 
        border-radius: 6px;
    }
'''

NONE_BORDER_BGCOLOR_BTN_THEME = '''
    QPushButton:!hover { 
        border: none; 
        background-color: none;  
    }
    QPushButton:hover {
        border: none; 
        background-color: none;  
    }
    QPushButton:focus {
        border: none; 
        background-color: none;        
    }
    QToolTip {
        padding: 0 1px;
        background: rgb(40,44,52);
        border: 1px solid rgb(171,178,191);
        opacity: 220;
        border-radius: 5px;  /* как убрать торчащие фоновые углы? */
    }
'''

TOOLBAR_THEME = '''
    QToolBar { 
        background: transparent;
    }
    
    QToolButton {
        padding: 10px;
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 6px;
    }
    
    QToolButton:hover {
        background-color: rgb(40,44,52);
    }
    
    QToolButton:pressed {
        border: 1px solid rgb(53,115,212);
    }

    QToolTip {
        padding: 0 1px;
        background: rgb(40,44,52);
        border: 1px solid rgb(171,178,191);
        opacity: 220;
        border-radius: 5px;  /* как убрать торчащие фоновые углы? */
    }
'''

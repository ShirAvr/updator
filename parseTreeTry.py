trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
arglist: argument (',' argument)*  [',']
argument: ( test [comp_for] |
            test ':=' test |
            test '=' test |
            '**' test |
            '*' test )
===================

trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME | our_var
arglist: argument (',' argument)*  [','] |
argument: ( test [comp_for] |
            test ':=' test |
            test '=' test |
            '**' test |
            '*' test |
            our_var )

our_var: UPDATOR_VAR


token:
UPDATOR_VAR: "$"[digit]
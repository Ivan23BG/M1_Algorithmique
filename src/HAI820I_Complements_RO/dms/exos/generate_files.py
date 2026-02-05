import os

template = """% ----- Consignes exo {xx} ----- %
\\begin{{td-exo}}[exo{xx}]\\, % {xx} 
	
\\end{{td-exo}}

% ----- Solutions exo {xx} ----- %
\\iftoggle{{showsolutions}}{{ 
	\\begin{{td-sol}}[]\\ % {xx}
		
	\\end{{td-sol}}
}}{{}}
"""

for i in range(1, 9):
    # if i == 2:
    #     continue

    filename = f"exo_{i:02d}.tex"
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(template.format(xx=i))

print("Done.")

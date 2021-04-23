import re
import csv
import pathlib
import pandas as pd
import numpy as np

VENDERS = [
    # "sunbird",
    "nlyte",
    "device42",
    "graphical_network",
]
TARGET = "Used the software for:"

def parse(csv_filepath: pathlib.Path) -> pd.DataFrame:
    """
    "Yoshihiro Fukuhara.IT Tech, (XXXX emploees)Used the software for: Less than 6 monthsOverall Rating..."
    もしくは
    Verified ReviewerIT Tech, (XXXX emploees)Used the software for: Less than 6 monthsOverall Rating..."
    
    1 "Used the software for:"よりも前の部分だけ切り出す
    2 ","よりも前の部分を切り出す
        2.1 Verified Reviewerにマッチする文字列を含む場合は名前は「Verified Reviewer」
        2.2 そうでなければ、最初の"."以前が名前
        2.3 名前以外の部分が業界
    3 ","よりも後ろを切り出す
        3.1 employeesにマッチする文字列がなければNan
        3.2 "XX-YY"の形なら従業員数は「YY」
        3.3 "XX+"の形なら従業員数は「XX」
    """
    columns = ["name", "domain", "employees"]
    df = pd.DataFrame(columns=columns)

    with open(str(csv_filepath)) as f:
        reader = csv.reader(f)
        for i, s in enumerate(reader):
            match= re.search("^.*?Used the software for:", s[0])
            if match:
                match_string = match.group()
            else:
                print(f"at line:{i+1}")
                raise ValueError
            
            formmer_half = match_string.split(",")[0]
            latter_half = match_string.replace(formmer_half+", ", "")
            
            # 名前とドメインを取得
            if re.search("^Verified Reviewer.*?", formmer_half):
                name = "Verified Reviewer"
                domain = formmer_half.replace(name, "")
            else:
                name = formmer_half.split(".")[0]
                domain = formmer_half.replace(name+".", "")

            # 従業員数を取得
            if re.search("-.*? employees", latter_half):
                employees = re.search("-.*? employees", latter_half).group()
                employees = employees.split("employees")[0]
                employees = employees.split("-")[-1]
                employees = employees.replace(",", "")
                employees = employees.replace(" ", "")
                employees = int(employees)
            elif re.search("^.*?\+ employees", latter_half):
                employees = latter_half.split("+ employees")[0]
                employees = employees.replace(",", "")
                employees = employees.replace(" ", "")
                employees = int(employees)
            else:
                employees = np.nan

            df = df.append({"name": name, "domain": domain, "employees": employees}, ignore_index=True)
    
    return df

if __name__ == "__main__":
    for vender in VENDERS:
        filepath = pathlib.Path(f"data/{vender}.csv")
        df = parse(filepath)
        print(df)
        df.to_csv(f"output/{vender}_output.csv")
import yaml, sys

with open(sys.argv[1], "r") as f:
    data = f.read()
    data = yaml.safe_load(data)

output = []
for i in data["fields"]:
    i = i.lower()
    if " " in i:
        output.append(i.replace(" ", "-"))
        output.append(i.replace(" ", "_"))
    if "-" in i:
        output.append(i.replace(" ", " "))
        output.append(i.replace(" ", "_"))
    if "_" in i:
        output.append(i.replace(" ", " "))
        output.append(i.replace(" ", "-"))

    output.append(i)
output = list(set(output))


class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

yaml.dump({"fields": output}, sys.stdout,
          Dumper=MyDumper,
          default_flow_style=False, sort_keys=True)

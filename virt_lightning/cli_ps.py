class CLIps:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "ps", help="List the VM currently running", parents=[parent_parser]
        )

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self

    @staticmethod
    def run(vmm, configuration, context="default", name=None, **kwargs):
        """Returns the status of the VM of the envionment."""

        results = {}

        for domain in vmm.list_domains():
            if context and context != domain.context:
                continue
            name = domain.name

            if not domain.ipv4:  # Not a VL managed VM
                continue

            results[name] = {
                "name": name,
                "ipv4": (domain.ipv4 and str(domain.ipv4.ip)) or "waiting",
                "context": domain.context,
                "username": domain.username,
                "distro": domain.distro,
            }

        output_template = "+ {name:<13}   {username}@{ipv4:>5} [{distro}]"
        for _, v in sorted(results.items()):
            print(output_template.format(**v))  # noqa: T001

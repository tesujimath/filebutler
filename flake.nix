{
  description = "Flake for filebutler environment";

  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs/nixpkgs-unstable;
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, flake-utils, nixpkgs }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        python3WithPackages =
          pkgs.python3.withPackages(ps: with ps; [
            # runtime:
            pytz
            setuptools
            tzlocal
            # for PyPI packaging:
            pip-tools
            twine
            wheel
          ]);

      in
        with pkgs;
        {
          devShells.default = mkShell {
            nativeBuildInputs = [
              python3WithPackages
            ];
          };
        }
    );
}

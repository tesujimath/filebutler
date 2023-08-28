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
            pytz
            setuptools
            tzlocal
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

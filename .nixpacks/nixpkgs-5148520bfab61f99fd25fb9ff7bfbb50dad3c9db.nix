{ pkgs }:

{
  deps = [
    pkgs.python39
    pkgs.python39Packages.pip
    pkgs.postgresql_16
    pkgs.gcc
  ];
}

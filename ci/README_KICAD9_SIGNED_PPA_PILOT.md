# Secure KiCad9 GitHub Actions install pilot — NO FAB/TX
Tests a direct signed APT source for KiCad 9.0 Ubuntu noble rather than
`add-apt-repository`, whose Launchpad API was throwing 500/504/disconnections.
The PPA public signing key is fetched over HTTPS and compared with known
**FDA854F61C4D0D9572BB95E5245D5502FAD7A805** before
using a scoped `Signed-By` keyring. APT still verifies signed repository
metadata; no untrusted repositories, no downgrade, no precomputed PASS.
Key fingerprint corroborated in historical KiCad community installation logs:
https://forum.kicad.info/t/update-to-kicad-version-9-not-working/58781
Official PPA source:
https://www.kicad.org/download/details/ubuntu/
Target version must be KiCad 9.0.x. No electrical files modified.
If successful, convert historic workflows to shared installer in a separate
infra PR, and rerun all native gates on final CAD SHA before merge. No FAB/TX.

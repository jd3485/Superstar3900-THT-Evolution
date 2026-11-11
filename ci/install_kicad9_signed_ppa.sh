#!/usr/bin/env bash
# Secure KiCad9 PPA installation pilot. Strict PPA key fingerprint and apt signature checks.
# NO FAB / NO TX; does not touch THT electrical design.
set -Eeuo pipefail
readonly KEY_FPR='FDA854F61C4D0D9572BB95E5245D5502FAD7A805'
# Alternate HTTPS keyservers; only the exact pinned key fingerprint is accepted.
readonly KEY_URL_PRIMARY="https://keys.openpgp.org/vks/v1/by-fingerprint/${KEY_FPR}"
readonly KEY_URL_SECONDARY="https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x${KEY_FPR}"
readonly PPA_URL="https://ppa.launchpadcontent.net/kicad/kicad-9.0-releases/ubuntu/"
readonly KEYRING="/usr/share/keyrings/kicad9-ppa-keyring.gpg"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ca-certificates curl gnupg
fetched=0
for key_url in "${KEY_URL_PRIMARY}" "${KEY_URL_SECONDARY}"; do
  if curl --retry 1 --retry-all-errors --retry-delay 2 --connect-timeout 12 --max-time 45 --fail --show-error --silent --location "${key_url}" --output "${tmpdir}/key.asc"; then
    fetched=1
    break
  fi
done
if [[ "${fetched}" != "1" ]]; then
  echo "FATAL: signing key could not be fetched from HTTPS keyservers; NO verification bypass" >&2
  exit 2
fi
actual="$(gpg --batch --show-keys --with-colons "${tmpdir}/key.asc" | awk -F: '$1=="fpr"{print toupper($10);exit}')"
if [[ "${actual}" != "${KEY_FPR}" ]]; then
  echo "FATAL: PPA signing key fingerprint mismatch: ${actual}" >&2
  exit 3
fi
gpg --batch --yes --dearmor --output "${tmpdir}/kicad-ppa.gpg" "${tmpdir}/key.asc"
sudo install -m 0644 "${tmpdir}/kicad-ppa.gpg" "${KEYRING}"
printf 'Types: deb\nURIs: %s\nSuites: noble\nComponents: main\nSigned-By: %s\n' "${PPA_URL}" "${KEYRING}" | sudo tee /etc/apt/sources.list.d/kicad9-signed.sources
sudo apt-get update -qq -o Acquire::Retries=3
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq -o Acquire::Retries=3 kicad
version="$(kicad-cli version)"
echo "KiCad CLI version: ${version}"
if [[ ! "${version}" =~ ^9\.0\.[0-9]+ ]]; then
 echo "FATAL: expected native KiCad 9.0.x" >&2
 exit 4
fi
echo "PASS_KICAD9_SIGNED_APT_PPA_PILOT key_fingerprint_verified_and_signed_inrelease_enforced"

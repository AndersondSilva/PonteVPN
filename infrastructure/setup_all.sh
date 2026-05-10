#!/bin/bash
# PonteVPN — Orquestrador de Provisionamento

echo "🌉 PonteVPN — Orquestrador de Servidores"
echo "Este script irá ajudar a provisionar os nós da rede."

read -p "Deseja provisionar o nó BR (São Paulo)? [y/N]: " PROV_BR
if [[ $PROV_BR == "y" ]]; then
    read -p "IP do servidor BR: " IP_BR
    read -p "Senha SSH: " PASS_BR
    python infrastructure/provision_remote.py $IP_BR root $PASS_BR "secret_ponte_br_2026"
fi

read -p "Deseja provisionar o nó PT (Lisboa)? [y/N]: " PROV_PT
if [[ $PROV_PT == "y" ]]; then
    read -p "IP do servidor PT: " IP_PT
    read -p "Senha SSH: " PASS_PT
    python infrastructure/provision_remote.py $IP_PT root $PASS_PT "secret_ponte_pt_2026"
fi

echo "✅ Processo de orquestração finalizado."

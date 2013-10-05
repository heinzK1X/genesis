# coding=utf-8
"""OpenVPN Plugin for Ajenti - Ported to Genesis by arkOS Team"""
MODULES = ['main', 'widget', 'config', 'backend']

DEPS = [
	(['any'],
	[
		('app', 'openvpn', 'openvpn'),
	])
]

NAME = 'OpenVPN'
ICON = 'gen-lock'
PLATFORMS = ['any']
DESCRIPTION = ''
VERSION = '2'
GENERATION = 1
AUTHOR = 'Ilya Voronin'
HOMEPAGE = 'https://github.com/ivoronin'

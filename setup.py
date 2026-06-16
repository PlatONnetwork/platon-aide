from setuptools import (
    setup,
    find_packages,
)


deps = {
    'platon-aide': [
        'web3>=5.23.0',
        'eth_account>=0.5.9',
        'eth_hash>=0.3.2',
        'eth_keys>=0.3.4',
        'eth_typing>=2.3.0',
        'eth_utils>=1.10.0',
        'rlp>=1.2.0',
        'gql>=3.0.0rc0',
    ]
}

with open('./README.md', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='platon_aide',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='2.0.1',
    description="""An aide that helps you quickly access the platon chain and use its basic functions.""",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='ssdut.steven',
    author_email='ssdut.steven@gmail.com',
    url='https://github.com/PlatONnetwork/platon-aide',
    include_package_data=True,
    install_requires=deps['platon-aide'],
    py_modules=['platon_aide'],
    extras_require=deps,
    license="MIT",
    zip_safe=False,
    package_data={'platon-aide': ['py.typed']},
    keywords='platon',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)

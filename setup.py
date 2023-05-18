from setuptools import (
    setup,
    find_packages,
)


deps = {
    'platon-aide': [
        'web3>=5.31.3',
        'eth_account>=0.8.0',
        'eth_hash>=0.5.1',
        'eth_keys>=0.4.0',
        'eth_typing>=3.2.0',
        'eth_utils>=2.1.0',
        'rlp>=1.2.0',
        'gql>=3.0.0rc0',
    ]
}

with open('./README.md', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='platon-aide',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='2.0.0',
    description="""An aide that helps you quickly access the platon chain and use its basic functions.""",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Steven',
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

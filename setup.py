from setuptools import (
    setup,
    find_packages,
)


deps = {
    'platon-aide': [
        'platon.py>=1.3.0',
        'platon_account>=1.2.0',
        'platon_hash>=1.2.0',
        'platon_keys>=1.2.0',
        'platon_typing>=1.2.0',
        'platon_utils>=1.2.0',
        'rlp>=1.2.0',
        'gql>=3.0.0rc0',
    ]
}

with open('./README.md', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='platon-aide',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='1.3.1',
    description="""An aide that helps you quickly access the platon chain and use its basic functions.""",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Shinnng',
    author_email='shinnng@outlook.com',
    url='https://github.com/shinnng/platon-aide',
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

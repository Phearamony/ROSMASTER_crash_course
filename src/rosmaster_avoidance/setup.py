from setuptools import setup

package_name = 'rosmaster_avoidance'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Phan Phearamony',
    maintainer_email='monypheara.jp@gmail.com',
    description='LiDAR obstacle avoidance node for the ROSMASTER A1',
    license='MIT',
    entry_points={
        'console_scripts': [
            # ros2 run rosmaster_avoidance lidar_avoidance
            'lidar_avoidance = rosmaster_avoidance.lidar_avoidance:main',
        ],
    },
)

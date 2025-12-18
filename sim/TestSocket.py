#!/usr/bin/env python3
"""
Connects to shotManager so you can send it messages. Fun times!
"""

import os
import socket
import struct
import sys
import threading
sys.path.append(os.path.realpath(".."))
import app_packet

# create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('10.1.48.157', 5507)
sock.connect(server_address)

# start listen thread
def listener(sock, verbose):
    current_packet = b""
    current_packet_length = 9999

    while True:
        data = sock.recv(1)

        current_packet += data
        if len(current_packet) == app_packet.SOLO_MESSAGE_HEADER_LENGTH:
            (current_packet_type, current_packet_length) = struct.unpack("<II", current_packet)

        if len(current_packet) == app_packet.SOLO_MESSAGE_HEADER_LENGTH + current_packet_length:
            value = current_packet[app_packet.SOLO_MESSAGE_HEADER_LENGTH:]

            if current_packet_type == app_packet.SOLO_MESSAGE_GET_CURRENT_SHOT:
                (shot,) = struct.unpack("<i", value)
                print("[App]: Received SOLO_MESSAGE_GET_CURRENT_SHOT")
                if verbose:
                    print("Shot ID: %d" % shot)

            elif current_packet_type == app_packet.SOLO_MESSAGE_LOCATION:
                (lat, lon, alt) = struct.unpack("<ddf", value)
                print("[App]: Received SOLO_MESSAGE_LOCATION")
                if verbose:
                    print("Location: %f, %f, %f" % (lat, lon, alt))

            elif current_packet_type == app_packet.SOLO_SPLINE_RECORD:
                print("[App]: Received SOLO_SPLINE_RECORD")

            elif current_packet_type == app_packet.SOLO_SPLINE_PLAY:
                print("[App]: Received SOLO_SPLINE_PLAY")

            elif current_packet_type == app_packet.SOLO_SPLINE_POINT:
                (index, lat, lon, alt, pitch, yaw, u_position, status) = struct.unpack(
                    "<Iddffffh", value
                )
                print("[App]: Received SOLO_SPLINE_POINT")
                if verbose:
                    print("Index: %d" % index)
                    print("Location: %f, %f, %f" % (lat, lon, alt))
                    print("Pitch, Yaw: %f, %f" % (pitch, yaw))
                    print("uPosition: %f" % u_position)
                    print("Status: %d" % status)

            elif current_packet_type == app_packet.SOLO_SPLINE_ATTACH:
                (index,) = struct.unpack("<I", value)
                print("[App]: Received SOLO_SPLINE_ATTACH")
                if verbose:
                    print("Index: %d" % index)

            elif current_packet_type == app_packet.SOLO_SPLINE_PLAYBACK_STATUS:
                (u_position, u_velocity) = struct.unpack("<ff", value)
                print("[App]: Received SOLO_SPLINE_PLAYBACK_STATUS")
                if verbose:
                    print("uPosition: %f" % u_position)
                    print("uVelocity: %f" % u_velocity)

            elif current_packet_type == app_packet.SOLO_SPLINE_PATH_STATUS:
                (min_time, max_time) = struct.unpack("<ff", value)
                print("[App]: Received SOLO_SPLINE_PATH_STATUS")
                if verbose:
                    print("minTime: %f" % min_time)
                    print("maxTime: %f" % max_time)

            elif current_packet_type == app_packet.GOPRO_V1_STATE:
                print("[App]: Received GOPRO_V1_STATE")

            elif current_packet_type == app_packet.GOPRO_V2_STATE:
                print("[App]: Received GOPRO_V2_STATE")

            else:
                print("[App]: Got an unknown packet type: %d" % current_packet_type)

            current_packet = b""


print("Verbose? y/n")
verbose = input(">").strip().lower() == "y"

w = threading.Thread(name="listener", target=listener, args=(sock, verbose), daemon=True)
w.start()

print("Please enter desired shot.")
print("0 = Selfie")
print("1 = Orbit")
print("2 = MP Cable Cam")
print("5 = Follow Me")
print("6 = Classic Cable Cam")
print("7 = Load a MP Cable")
shot = int(input(">"))
step = 0

# main "app" loop
while True:
    if shot == 0:
        packet = struct.pack("<III", app_packet.SOLO_MESSAGE_SET_CURRENT_SHOT, 4, shot)
        sock.sendall(packet)
    elif shot == 1:
        packet = struct.pack("<III", app_packet.SOLO_MESSAGE_SET_CURRENT_SHOT, 4, shot)
        sock.sendall(packet)
    elif shot == 2:
        if step == 0:
            a_count = 0
            b_count = 0
            packet = struct.pack("<III", app_packet.SOLO_MESSAGE_SET_CURRENT_SHOT, 4, shot)
            sock.sendall(packet)
            step += 1
        elif step == 1:
            print("Please press A or B button.")
            button = input(">")
            if button == "A":
                packet = struct.pack("<II", app_packet.SOLO_RECORD_POSITION, 0)
                sock.sendall(packet)
                a_count += 1
            elif button == "B":
                packet = struct.pack("<II", app_packet.SOLO_RECORD_POSITION, 0)
                sock.sendall(packet)
                packet = struct.pack("<II", app_packet.SOLO_SPLINE_PLAY, 0)
                sock.sendall(packet)
                packet = struct.pack("<III", app_packet.SOLO_SPLINE_ATTACH, 4, a_count)
                sock.sendall(packet)
                packet = struct.pack("<IIhf", app_packet.SOLO_SPLINE_PATH_SETTINGS, 6, 0, 20)
                sock.sendall(packet)
                step += 1
        elif step == 2:
            _ = input("Hit enter to send SEEK.")
            packet = struct.pack("<IIf", app_packet.SOLO_SPLINE_SEEK, 4, 0.5)
            sock.sendall(packet)
            step += 1
    elif shot == 5:
        packet = struct.pack("<III", app_packet.SOLO_MESSAGE_SET_CURRENT_SHOT, 4, shot)
        sock.sendall(packet)
    elif shot == 6:
        packet = struct.pack("<III", app_packet.SOLO_MESSAGE_SET_CURRENT_SHOT, 4, shot)
        sock.sendall(packet)
    elif shot == 7:
        if step == 0:
            packet = struct.pack("<III", app_packet.SOLO_MESSAGE_SET_CURRENT_SHOT, 4, 2)
            sock.sendall(packet)
            packet = struct.pack(
                "<IIIddffffh",
                app_packet.SOLO_SPLINE_POINT,
                38,
                0,
                37.330674,
                -122.028759,
                15,
                0,
                90,
                0,
                0,
            )
            sock.sendall(packet)
            packet = struct.pack(
                "<IIIddffffh",
                app_packet.SOLO_SPLINE_POINT,
                38,
                1,
                37.331456,
                -122.027785,
                15,
                0,
                45,
                0,
                0,
            )
            sock.sendall(packet)
            packet = struct.pack(
                "<IIIddffffh",
                app_packet.SOLO_SPLINE_POINT,
                38,
                2,
                37.332216,
                -122.027842,
                15,
                0,
                0,
                0,
                0,
            )
            sock.sendall(packet)
            packet = struct.pack("<II", app_packet.SOLO_SPLINE_PLAY, 0)
            sock.sendall(packet)
            packet = struct.pack("<III", app_packet.SOLO_SPLINE_ATTACH, 4, 0)
            sock.sendall(packet)
            step += 1

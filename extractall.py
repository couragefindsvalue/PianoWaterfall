import os
import json
import mido


def extract_all_midis():
    # 获取当前文件夹路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    songs_data = {}

    print(f"📁 正在扫描目录: {current_dir}")

    # 遍历当前目录下的所有文件
    for filename in os.listdir(current_dir):
        if filename.lower().endswith(('.mid', '.midi')):
            file_path = os.path.join(current_dir, filename)
            song_name = os.path.splitext(filename)[0]  # 去掉后缀作为歌名

            print(f"🎵 正在解析: {song_name} ...")
            try:
                mid = mido.MidiFile(file_path)
                merged_track = mido.merge_tracks(mid.tracks)

                notes_data = []
                current_time = 0.0
                active_notes = {}

                for msg in merged_track:
                    current_time += mido.tick2second(msg.time, mid.ticks_per_beat, 500000)

                    if msg.type == 'note_on' and msg.velocity > 0:
                        active_notes[msg.note] = current_time
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        if msg.note in active_notes:
                            start_time = active_notes.pop(msg.note)
                            duration = current_time - start_time

                            # 过滤超短音和超出音域的音符
                            if duration > 0.05 and 21 <= msg.note <= 108:
                                notes_data.append({
                                    'pitch': msg.note,
                                    'start': round(start_time, 3),
                                    'duration': round(duration, 3)
                                })

                if notes_data:
                    # 按时间排序
                    notes_data.sort(key=lambda x: x['start'])
                    songs_data[song_name] = notes_data
                    print(f"   ✅ 成功提取 {len(notes_data)} 个音符")
                else:
                    print(f"   ⚠️ 跳过：没有找到有效音符")

            except Exception as e:
                print(f"   ❌ 解析失败: {e}")

    # 保存为 JSON
    output_file = os.path.join(current_dir, "songs.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(songs_data, f, ensure_ascii=False, separators=(',', ':'))

    print(f"\n🎉 全部完成！共收录 {len(songs_data)} 首歌，数据已保存至: {output_file}")


if __name__ == "__main__":
    extract_all_midis()
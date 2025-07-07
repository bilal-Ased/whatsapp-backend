import json

# Your TN numbers as a string (you can paste them here)
tn_numbers_text = """TN069100
TN946600
TN155100
TN048400
TN998000
TN277040
TN565200
TN112300
TN180400
TN555800
TN199400
TN504500
TN415230
TN034940
TN130430
TN238900
TN723300
TN097900
TN019140
TN142400
TN009100
TN283000
TN881500
TN309400
TN998800
TN130430
TN241150
TN013800
TN994400
TN793600
TN429630
TN268800
TN438100
TN179700
TN248960
TN113700
TN727100
TN684400
TN261060
TN293800
TN487360
TN881500
TN279700
TN001700
TN137150
TN713240
TN197700
TN529150
TN412000
TN186200
TN948300
TN031360
TN410000
TN001700
TN783400
TN261600
TN479300
TN245300
TN727600
TN402600
TN009660
TN551800
TN385400
TN854800
TN529000
TN287200
TN213100
TN498700
TN438400
TN029950
TN282600
TN817600
TN226050
TN207700
TN857900
TN240200
TN778270
TN604960
TN019500
TN723500
TN551800
TN633500
TN956160
TN788350
TN441700
TN318140
TN029950
TN477800
TN024400
TN095800
TN327000
TN855870
TN346900
TN944900
TN097700
TN484400
TN883100
TN122000
TN225000
TN208800
TN463300
TN406160
TN067100
TN897470
TN610820
TN244480
TN716000
TN656000
TN906020
TN953100
TN745540
TN059600
TN752400
TN383000
TN592900
TN159100
TN199680
TN309760
TN556800
TN446460
TN818900
TN360400
TN364200
TN036600
TN795360
TN053600
TN508400
TN219600
TN360400
TN661120
TN697600
TN742800
TN949630
TN903550
TN333800
TN255200
TN542100
TN883440
TN698600
TN438800
TN559300
TN875800
TN055740
TN582500
TN622800
TN772000
TN723720
TN051260
TN556800
TN335400
TN806300
TN723500
TN523900
TN372200
TN485500
TN901800
TN723720
TN661120
TN436800
TN959700
TN834200
TN007900
TN850800
TN087400
TN596100
TN961300
TN107500
TN559300
TN549500
TN797760
TN766850
TN322300
TN077060
TN288900
TN095800
TN149900
TN151500
TN184400
TN274200
TN163800
TN109040
TN144300
TN665540
TN285100
TN026700
TN689860
TN514200
TN994100
TN326100
TN526200
TN726500
TN078600
TN273900
TN116900
TN262100
TN158600
TN262900
TN753100
TN726500
TN676800
TN400030
TN913500
TN457600
TN043800
TN021400/DTB001427
TN831900
TN797760
TN451200
TN924670
TN586600
TN536900
TN077600
TN271900
TN761300
TN940800
TN577600
TN518880
TN918940
TN955550
TN831900
TN103700
TN273900
TN484000
TN843600
TN113900
TN958750
TN081500
TN106750
TN695200
TN247200
TN735200
TN170940
TN502500
TN443300
TN521200
TN157900
TN622900
TN697700
TN653500
TN431900
TN995900
TN811200
TN051300
TN791940
TN040500
TN626940
TN000539
TN489500
TN118800
TN102700
TN000514
TN000510
TN184500
TN865200
TN000501
TN477800
TN000489
TN000485
TN000479
TN000476
TN000475
TN007800
TN314050
TN160700
TN051300
TN000472"""

def process_tn_numbers(tn_text):
    """Extract numbers from TN codes, removing 'TN' prefix"""
    numbers = []
    for line in tn_text.strip().split('\n'):
        line = line.strip()
        if line.startswith('TN'):
            # Handle special case like "TN021400/DTB001427"
            if '/' in line:
                number = line.split('/')[0][2:]  # Remove TN and take part before /
            else:
                number = line[2:]  # Remove TN prefix
            numbers.append(number)
    return numbers

def find_matches_in_json(json_file_path, tn_numbers):
    """Find matches between TN numbers and last 6 digits of ticket numbers in JSON"""
    matches = []
    no_matches = []
    
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Handle both single object and array of objects
        if isinstance(data, dict):
            data = [data]
        
        # Create a mapping of last 6 digits to ticket records
        ticket_map = {}
        for record in data:
            if 'Ticket_number' in record:
                ticket_number = str(record['Ticket_number'])
                last_6_digits = ticket_number[-6:]
                if last_6_digits not in ticket_map:
                    ticket_map[last_6_digits] = []
                ticket_map[last_6_digits].append(record)
        
        # Check each TN number for matches
        for tn_number in tn_numbers:
            # Get last 6 digits of TN number
            tn_last_6 = tn_number[-6:] if len(tn_number) >= 6 else tn_number
            
            if tn_last_6 in ticket_map:
                for matching_record in ticket_map[tn_last_6]:
                    matches.append({
                        'tn_number': tn_number,
                        'tn_last_6': tn_last_6,
                        'ticket_number': matching_record['Ticket_number'],
                        'ticket_last_6': str(matching_record['Ticket_number'])[-6:],
                        'record': matching_record
                    })
            else:
                no_matches.append({
                    'tn_number': tn_number,
                    'tn_last_6': tn_last_6
                })
    
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file_path}' not found.")
        return [], []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{json_file_path}'.")
        return [], []
    
    return matches, no_matches

def main():
    # Process TN numbers
    tn_numbers = process_tn_numbers(tn_numbers_text)
    print(f"Processed {len(tn_numbers)} TN numbers")
    
    # Print all TN numbers with TN removed
    print("\n=== TN NUMBERS (TN PREFIX REMOVED) ===")
    for i, number in enumerate(tn_numbers, 1):
        print(f"{i:3d}. {number}")
    print("=" * 50)
    
    # Specify your JSON file path here
    json_file_path = "/Users/bilalmughal/Documents/Dev/outbound-backend/response.txt"
    
    # Find matches
    matches, no_matches = find_matches_in_json(json_file_path, tn_numbers)
    
    # Display results
    print(f"\n=== MATCHES FOUND: {len(matches)} ===")
    for match in matches:
        print(f"TN: {match['tn_number']} -> Ticket: {match['ticket_number']}")
        print(f"  Last 6 digits match: {match['tn_last_6']}")
        print(f"  Customer: {match['record'].get('Customer_Name', 'N/A')}")
        print(f"  Status: {match['record'].get('Ticket_Status', 'N/A')}")
        print("-" * 50)
    
    print(f"\n=== NO MATCHES FOUND: {len(no_matches)} ===")
    for no_match in no_matches[:10]:  # Show first 10 to avoid clutter
        print(f"TN: {no_match['tn_number']} (last 6: {no_match['tn_last_6']})")
    
    if len(no_matches) > 10:
        print(f"... and {len(no_matches) - 10} more")
    
    # Save matches to file
    if matches:
        with open('matches_found.json', 'w') as f:
            json.dump(matches, f, indent=2)
        print(f"\nMatches saved to 'matches_found.json'")

if __name__ == "__main__":
    main()
    
    
    
    
    



 

 31. 429630
 32. 268800
 33. 438100
 34. 179700
 35. 248960
 36. 113700
 37. 727100
 38. 684400
 39. 261060
 40. 293800
 41. 487360
 42. 881500
 43. 279700
 44. 001700
 45. 137150
 46. 713240
 47. 197700
 48. 529150
 49. 412000
 50. 186200
 51. 948300
 52. 031360
 53. 410000
 54. 001700
 55. 783400
 56. 261600
 57. 479300
 58. 245300
 59. 727600
 60. 402600
 61. 009660
 62. 551800
 63. 385400
 64. 854800
 65. 529000
 66. 287200
 67. 213100
 68. 498700
 69. 438400
 70. 029950
 71. 282600
 72. 817600
 73. 226050
 74. 207700
 75. 857900
 76. 240200
 77. 778270
 78. 604960
 79. 019500
 80. 723500
 81. 551800
 82. 633500
 83. 956160
 84. 788350
 85. 441700
 86. 318140
 87. 029950
 88. 477800
 89. 024400
 90. 095800
 91. 327000
 92. 855870
 93. 346900
 94. 944900
 95. 097700
 96. 484400
 97. 883100
 98. 122000
 99. 225000
100. 208800
101. 463300
102. 406160
103. 067100
104. 897470
105. 610820
106. 244480
107. 716000
108. 656000
109. 906020
110. 953100
111. 745540
112. 059600
113. 752400
114. 383000
115. 592900
116. 159100
117. 199680
118. 309760
119. 556800
120. 446460
121. 818900
122. 360400
123. 364200
124. 036600
125. 795360
126. 053600
127. 508400
128. 219600
129. 360400
130. 661120
131. 697600
132. 742800
133. 949630
134. 903550
135. 333800
136. 255200
137. 542100
138. 883440
139. 698600
140. 438800
141. 559300
142. 875800
143. 055740
144. 582500
145. 622800
146. 772000
147. 723720
148. 051260
149. 556800
150. 335400
151. 806300
152. 723500
153. 523900
154. 372200
155. 485500
156. 901800
157. 723720
158. 661120
159. 436800
160. 959700
161. 834200
162. 007900
163. 850800
164. 087400
165. 596100
166. 961300
167. 107500
168. 559300
169. 549500
170. 797760
171. 766850
172. 322300
173. 077060
174. 288900
175. 095800
176. 149900
177. 151500
178. 184400
179. 274200
180. 163800
181. 109040
182. 144300
183. 665540
184. 285100
185. 026700
186. 689860
187. 514200
188. 994100
189. 326100
190. 526200
191. 726500
192. 078600
193. 273900
194. 116900
195. 262100
196. 158600
197. 262900
198. 753100
199. 726500
200. 676800
201. 400030
202. 913500
203. 457600
204. 043800
205. 021400
206. 831900
207. 797760
208. 451200
209. 924670
210. 586600
211. 536900
212. 077600
213. 271900
214. 761300
215. 940800
216. 577600
217. 518880
218. 918940
219. 955550
220. 831900
221. 103700
222. 273900
223. 484000
224. 843600
225. 113900
226. 958750
227. 081500
228. 106750
229. 695200
230. 247200
231. 735200
232. 170940
233. 502500
234. 443300
235. 521200
236. 157900
237. 622900
238. 697700
239. 653500
240. 431900
241. 995900
242. 811200
243. 051300
244. 791940
245. 040500
246. 626940
247. 000539
248. 489500
249. 118800
250. 102700
251. 000514
252. 000510
253. 184500
254. 865200
255. 000501
256. 477800
257. 000489
258. 000485
259. 000479
260. 000476
261. 000475
262. 007800
263. 314050
264. 160700
265. 051300
266. 000472




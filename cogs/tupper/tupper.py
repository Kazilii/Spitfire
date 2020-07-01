from redbot.core import commands
from redbot.core import Config
from redbot.core import checks
from discord import TextChannel as channel
from discord import File
from discord import Embed
from discord import NotFound
from validators import url as URL
from PIL import Image
import requests
from io import BytesIO
import json
from discord import Game
from .imagemanip import Avatar

PATH = '/home/dawn/bots/spitfire/'

class Tupper(commands.Cog):
	"""Future tupperware commands"""

	def __init__(self, bot):
		self.config = Config.get_conf(self, identifier=20211616518)
		default_channel = {
			'id': None,
			'token': None
		}
		default_user = {}
		self.config.register_channel(**default_channel)
		self.config.register_user(**default_user)
		self.bot = bot
		self.tupnotfound = 'Tulpa not found! Please check spelling or register Tulpa with `%tup register`'
		self.statusset = False

	@commands.command()
	async def webhooktest(self, ctx):
		hook = await channel.create_webhook(ctx.channel, name='Test')
		await hook.send('Hi there!', username="Not Kaz")
		await hook.delete()

	@commands.group()
	async def tup(self, ctx):
		"""Tupper management, use the following commands to manage your tulpa."""
		pass

	#@tup.command()
	#async def test(self, ctx):
	#	tup = self.config.user(ctx.author)
	#	for x in await tup.get_raw():
	#		if await tup.get_raw(x, 'prefix') == '{':
	#			await ctx.send('Prefix found')
	#		else:
	#			await ctx.send('Not found')
	#
	#				if await self.config.user(ctx.author).get_raw(x, y, 'prefix') == '{':
	#					await ctx.send('Prefix found')

	@tup.command()
	async def register(self, ctx, *, name):
		"""Register a tulpa. EX: %tup register Cool Tulpa"""
		tup = self.config.user(ctx.author)
		if await self.tuppercheck(ctx.author, name):
			await ctx.send('You have already registered a tulpa with that name! Nice try though!')
			return
		await tup.set_raw(name, 'name', value=name)
		await tup.set_raw(name, 'prefix', value=None)
		await tup.set_raw(name, 'suffix', value=None)
		await tup.set_raw(name, 'avatar', value='https://discordapp.com/assets/dd4dbc0016779df1378e7812eabaa04d.png')
		await tup.set_raw(name, 'pronouns', value=None)
		await tup.set_raw(name, 'description', value=None)
		await tup.set_raw(name, 'birthday', value=None)
		await ctx.send(
			'{name} registered! Please set the proxy with `%tup proxy`\nExample: `%tup proxy [text] {name}`'.format(
				name=name))
		return

	@tup.command()
	async def proxy(self, ctx, proxy, *, name):
		"""Assign a proxy to a tulpa. Proxies can not have spaces, but can be multiple characters. EX: %tup proxy [text] Cool Tulpa"""
		tup = self.config.user(ctx.author)
		if 'text' not in proxy:
			await ctx.send(
				'Invalid proxy. Proxies must have `text` in them somewhere.\nExample `%tup proxy {text} Cool Tulpa`\n`%tup proxy ~text~ Cool Tulpa`\n`%tup proxy StextS Cool Tulpa`')
			return
		if proxy == 'text':
			await ctx.send(
				'No proxy character found, make sure to specify which character is the proxy.\nExample `%tup proxy {text} Cool Tulpa`\n`%tup proxy ~text~ Cool Tulpa`\n`%tup proxy StextS Cool Tulpa`')
			return

		if proxy == '||text||':
			await ctx.send('That proxy is recognized by Discord as the spoiler tag, as such it is invalid.')
			return

		if proxy.startswith('<') and proxy.endswith('>'):
			await ctx.send('That proxy is recognized by Discord for various formatting purposes, as such it is invalid')
			return

		head, sep, tail = proxy.partition('text')

		for x in await tup.get_raw():
			if await tup.get_raw(x, 'prefix') == head and await tup.get_raw(x, 'suffix') == tail:
				await ctx.send('Another Tulpa in your system is already using that prefix!')
				return
		if await self.tuppercheck(ctx.author, name):
			await tup.set_raw(name, 'prefix', value=head)
			await tup.set_raw(name, 'suffix', value=tail)
			await ctx.send('Proxy set!')
			return
		await ctx.send(self.tupnotfound)
		return

	@tup.command()
	async def pronouns(self, ctx, pronouns, *, name):
		"""Sets the pronouns of a Tulpa, in they/them format. Example: %tup pronouns she/her Destiny"""
		tup = self.config.user(ctx.author)

		if await self.tuppercheck(ctx.author, name):
			await tup.set_raw(name, 'pronouns', value=pronouns)
			await ctx.send('Pronouns set to {}, for {}'.format(pronouns, name))
		else:
			await ctx.send(self.tupnotfound)

	@tup.command()
	async def birthday(self, ctx, birthday, *, name):
		"""Sets the birthday of a Tulpa, in MM/DD/YYYY format. Example: %tup birthday 04/01/2003"""
		if await self.tuppercheck(ctx.author, name):
			await self.config.user(ctx.author).set_raw(name, 'birthday', value=birthday)
			await ctx.send('Birthday for {tulpa} set to {birthday}'.format(tulpa=name, birthday=birthday))
		else:
			await ctx.send(self.tupnotfound)

	@tup.command()
	async def info(self, ctx, *, name):
		"""Displays information about this given tulpa"""
		tup = self.config.user(ctx.author)
		if await self.tuppercheck(ctx.author, name):
			embed = Embed(title=name)
			embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
			if await tup.get_raw(name, 'avatar') is not None:
				embed.set_thumbnail(url=await tup.get_raw(name, 'avatar'))
			if await tup.get_raw(name, 'prefix') is not None:
				embed.add_field(name='Proxy',
								value='{prefix}text{suffix}'.format(prefix=await tup.get_raw(name, 'prefix'),
																	suffix=await tup.get_raw(name, 'suffix')))
			if await tup.get_raw(name, 'pronouns') is not None:
				embed.add_field(name='Pronouns', value=await tup.get_raw(name, 'pronouns'))
			if await tup.get_raw(name, 'birthday') is not None:
				embed.add_field(name='Birthday', value=await tup.get_raw(name, 'birthday'))
			if await tup.get_raw(name, 'description') is not None:
				embed.add_field(name='Description', value=await tup.get_raw(name, 'description'))
			await ctx.send(embed=embed)
		else:
			await ctx.send(self.tupnotfound)

	@tup.command()
	async def list(self, ctx):
		"""Lists all Tulpa you have registered."""
		ls = []
		for x in await self.config.user(ctx.author).get_raw():
			ls.append(x)
		stri = "```\n"
		num = 1
		for x in ls:
			stri = stri + '{num}) {tup}\n'.format(num=num, tup=x)
			num = num + 1
		stri = stri + '```'
		await ctx.send(stri)

	@tup.command()
	async def description(self, ctx, *, description, name=None):
		"""Set the description of a Tulpa."""
		tup = self.config.user(ctx.author)
		for x in await tup.get_raw():
			if x in description and description.endswith(x):
				await tup.set_raw(x, 'description', value=description.rstrip(x))
				await ctx.send('Done, description set for {}'.format(x))

	@tup.command()
	async def avatar(self, ctx, *, url, name=None):
		"""Set the avatar of a Tulpa, provide url or attach an image file to command."""
		tup = self.config.user(ctx.author)
		if url.count(' ') >= 1:
			head, sep, tail = url.partition(' ')
			if URL(head):
				try:
					imgf = requests.get(head)
					img = Image.open(BytesIO(imgf.content))
					if not Avatar.checksize(pilimage=img, size=(128, 128)):
						Avatar.resize(pilimage=img, size=(128, 128)).save(PATH + 'tempimg.png')
						chnl = self.bot.get_channel(534534949030592513)
						imgmsg = await chnl.send(file=File(fp=PATH + 'tempimg.png', filename='image.png'))
						img = imgmsg.attachments[0].url
						head = img
					for x in await tup.get_raw():
						if x == tail:
							await tup.set_raw(tail, 'avatar', value=head)
							await ctx.send('Avatar set for {}'.format(tail))
							return
					await ctx.send(self.tupnotfound)
					return
				except:
					await ctx.send('Url or attachment are not a valid image.')
					return

		if not URL(url):
			for x in await tup.get_raw():
				if x == url:
					if len(ctx.message.attachments) > 0:
						await ctx.message.attachments[0].save(PATH + 'tempimg.png')
						try:
							img = Image.open(PATH + 'tempimg.png')
						except:
							await ctx.send('Attached file is not a valid image.')
							return
						if not Avatar.checksize(filepath=PATH + 'tempimg.png'):
							Avatar.resize(filepath=PATH + 'tempimg.png', size=(128, 128)).save(PATH + 'tempimg.png')
						chnl = self.bot.get_channel(534534949030592513)
						imgmsg = await chnl.send(file=File(fp=PATH + 'tempimg.png', filename='image.png'))
						img = imgmsg.attachments[0].url
						await tup.set_raw(url, 'avatar', value=img)
						await ctx.send('Avatar set for {}'.format(url))
						return
					else:
						await ctx.send('No image url or attachment found.')
						return
			await ctx.send(self.tupnotfound)
			return
		else:
			await ctx.send(
				'Please specify the Tulpa you want to change the avatar of.\nExample: `%tup avatar http://www.somesite.com/image.png Cool Tulpa`\nOr `%tup avatar Cool Tulpa` with an image attached.')
			return

	@tup.command()
	async def remove(self, ctx, *, name):
		tup = self.config.user(ctx.author)
		await tup.clear_raw(name)
		await ctx.send('{} has been removed'.format(name))

	@tup.command(aliases=["rename"])
	async def name(self, ctx, *, newname, oldname=None):
		"""Change the name of a Tulpa."""
		tup = self.config.user(ctx.author)
		for x in await tup.get_raw():
			if newname == x:
				await ctx.send("You need to supply a new name! Example: `%tup name NEWNAME OLDNAME`")
				return
			elif newname.endswith(x):
				for y in await tup.get_raw(x):
					await tup.set_raw(newname.rstrip(x).rstrip(' '), y, value=await tup.get_raw(x, y))
				await tup.set_raw(newname.rstrip(x).rstrip(' '), 'name', value=newname.rstrip(x))
				await tup.clear_raw(x)
				await ctx.send('Tulpa renamed to: {}'.format(newname.rstrip(x)))
				return
		await ctx.send(self.tupnotfound)
		return

	@tup.command(name="import")
	async def importtulpa(self, ctx):
		"""Import all of your Tulpa from PluralKit.\nInstructions\n1. DM @PluralKit#4020 with the command `pk;export`\n2. Download the .json file sent by PluralKit\n3. DM @Spitfire#1460 with the command `%tup import` and attach the json file."""
		tup = self.config.user(ctx.author)
		if len(ctx.message.attachments) < 1:
			await ctx.send_help()
			return
		await ctx.message.attachments[0].save(PATH + 'import.json')

		with open(PATH + 'import.json') as j:
			cur = 0
			pk = json.load(j)
			for x in pk['members']:
				if pk['members'][cur]['prefix'] is None and pk['members'][cur]['suffix'] is None:
					pass
				elif pk['members'][cur]['prefix'] == '' and pk['members'][cur]['suffix'] == '':
					pass
				else:
					await tup.set_raw(pk['members'][cur]['name'], 'name', value=pk['members'][cur]['name'])
					await tup.set_raw(pk['members'][cur]['name'], 'avatar', value=pk['members'][cur]['avatar_url'])
					if pk['members'][cur]['prefix'] is None:
						await tup.set_raw(pk['members'][cur]['name'], 'prefix', value='')
					else:
						await tup.set_raw(pk['members'][cur]['name'], 'prefix', value=pk['members'][cur]['prefix'])
					if pk['members'][cur]['suffix'] is None:
						await tup.set_raw(pk['members'][cur]['name'], 'suffix', value='')
					else:
						await tup.set_raw(pk['members'][cur]['name'], 'suffix', value=pk['members'][cur]['suffix'])
					await tup.set_raw(pk['members'][cur]['name'], 'birthday', value=None)
					await tup.set_raw(pk['members'][cur]['name'], 'pronouns', value=pk['members'][cur]['pronouns'])
					await tup.set_raw(pk['members'][cur]['name'], 'description',
									  value=pk['members'][cur]['description'])
					cur = cur + 1
			await ctx.send(
				'Tulpa imported! Please check to see if every Tulpa was imported successfully with the `%list` command!')

		# TODO Add importing functionality. See next comment
		'''
		This should be done by having the user DM PluralKit and using the command `pk;export`, then DM Spitfire, -
		and use the command `%tup import` with the json file attached.
		in other words. User DM's PluralKit `pk;export`, PluralKit sends system.json. User downloads system.json and DM's
		Spitfire `%tup import` with the system.json attached.
		If the user doesn't attach the system.json file, Spitfire will ask them to send the file.
		When setting up importing for ES, remove PluralKit from the server and setup a separate server for importing.
		This will prevent Tulpa messages from being duplicated
		'''

	@commands.command(hidden=True)
	async def bottest(self, ctx):
		await ctx.send('```{}```'.format(self.bot.user.id))
		await ctx.send('```{}```'.format(ctx.guild.get_member(self.bot.user.id).activity))

	async def tuppercheck(self, author, tupper):
		for x in await self.config.user(author).get_raw():
			if x == tupper:
				return True
		return False

	def statuscheck(self, message):
		if message.guild.get_member(self.bot.user.id).activity is not None:
			return True
		else:
			return False

	async def on_message(self, message):
		chan = self.config.channel(message.channel)
		if message.guild is None:
			return
		if message.author == self.bot.user:
			return

		if not self.statuscheck(message):
			game = Game(name='%help')
			await self.bot.change_presence(activity=game)

		if await chan.id() is None:
			hook = await message.channel.create_webhook(name='FireHook: {}'.format(message.channel.name), avatar=requests.get(self.bot.user.avatar_url).content)
			await chan.id.set(hook.id)

		try:
			await self.bot.get_webhook_info(await chan.id())
		except NotFound:
			hook = await message.channel.create_webhook(name='Firehook: {}'.format(message.channel.name), avatar=requests.get(self.bot.user.avatar_url).content)
			await chan.id.set(hook.id)

		if len(await self.config.user(message.author).get_raw()) > 0:
			for x in await self.config.user(message.author).get_raw():
				prefix = self.config.user(message.author).get_raw(x, 'prefix')
				suffix = self.config.user(message.author).get_raw(x, 'suffix')
				if await self.config.user(message.author).get_raw(x, 'prefix') is None:
					pass
				else:
					avatar = None
					if message.content.startswith(
							await self.config.user(message.author).get_raw(x, 'prefix')) and message.content.endswith(
							await self.config.user(message.author).get_raw(x, 'suffix')):
						if len(message.mentions) > 0:
							if len(message.content) == len(message.mentions[0]):
								return
						if message.content.startswith('||') and message.content.endswith('||'):
							return
						if message.content.startswith('<') and message.content.endswith('>'):
							return
						if message.content.startswith(await prefix + await prefix) and message.content.endswith(await suffix + await suffix):
							return
						hook = await self.bot.get_webhook_info(await chan.id())
						if await self.config.user(message.author).get_raw(x, 'avatar') is not None:
							avatar = await self.config.user(message.author).get_raw(x, 'avatar')
						await hook.send(content=message.content.lstrip(
							await self.config.user(message.author).get_raw(x, 'prefix')).rstrip(
							await self.config.user(message.author).get_raw(x, 'suffix')), username=x, avatar_url=avatar)
						if len(message.attachments) > 0:
							await message.attachments[0].save(PATH + 'tempimg')
							await message.channel.send(
								file=File(fp=PATH + 'tempimg', filename=message.attachments[0].filename))
						await message.delete()

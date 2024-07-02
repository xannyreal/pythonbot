import discord
import random
import string
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

# Bot başlatıldığında çalışacak kodlar
@bot.event
async def on_ready():
    guilds_info = '\n'.join(f"{guild.name} (ID: {guild.id})" for guild in bot.guilds)
    print(f'\n\n{bot.user.name} şu sunucularda aktif:\n{guilds_info}')

    await bot.change_presence(activity=discord.Game(name="coded by xannyreal"))

# Kullanıcı yetkilendirme kontrolü
@bot.check
async def globally_check(ctx):
    if hasattr(bot, 'create_role'):
        if bot.create_role in ctx.author.roles or ctx.author.guild_permissions.administrator:
            return True
        else:
            embed = discord.Embed(title="Yetki Hatası", description="Bu komutu kullanmak için yeterli yetkiye sahip değilsiniz.", color=0xff0000)
            await ctx.send(embed=embed)
            return False
    else:
        return True

# Log kanalı var mı kontrolü
async def log_channel_check(ctx):
    if not hasattr(bot, 'log_channel'):
        embed = discord.Embed(title="Log Kanalı Ayarlanmamış", description="Kullanıcı adı ve şifre göndermek için önce bir log kanalı ayarlamalısınız.\n.create-log #kanal", color=0xff0000)
        await ctx.send(embed=embed)
        return False
    return True

# Random şifre oluşturma
def generate_password():
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(5))  # 5 karakter uzunluğunda rastgele şifre
    return password

# Kullanıcı adı ve şifre gönderme komutu
@bot.command()
async def gönder(ctx, user: discord.User, username: str):
    if not await log_channel_check(ctx):
        return
    
    if not hasattr(bot, 'create_role'):
        embed = discord.Embed(title="Rol Ayarlanmamış", description="Komutu kullanabilecek bir rol ayarlayın.\n.create-rol @rol", color=0xff0000)
        await ctx.send(embed=embed)
        return
    
    password = generate_password()  # Random şifre oluştur
    embed = discord.Embed(title="Kullanıcı Adı ve Şifre Gönderildi", color=0x00ff00)
    embed.add_field(name="Kullanıcı", value=user.mention, inline=False)
    embed.add_field(name="Kullanıcı Adı", value=username, inline=False)
    embed.add_field(name="Şifre", value=password, inline=False)
    
    await ctx.send(embed=embed)
    
    try:
        await user.send(f"Kullanıcı Adı: {username}\nŞifre: {password}\nGönderen: {ctx.author}")
    except discord.Forbidden:
        await ctx.send(f"{user.mention} kullanıcısının DM'ine mesaj gönderilemedi. Kullanıcının DM almak için bot mesaj izinlerini kontrol edin.")

    if hasattr(bot, 'log_channel'):
        log_embed = discord.Embed(
            title="Kullanıcı Adı ve Şifre Gönderildi",
            description=f"{ctx.author.mention} kullanıcısı {ctx.channel.mention} kanalında {user.mention} kullanıcısına yeni bir kullanıcı adı ve şifre gönderdi.",
            color=0x00ff00
        )
        await bot.log_channel.send(embed=log_embed)

# Yalnızca yöneticilere özel rol oluşturma komutu
@bot.command(name='create-rol')
@commands.has_permissions(administrator=True)
async def create_rol(ctx, *, role: discord.Role):
    bot.create_role = role
    embed = discord.Embed(title="Rol Ayarlandı", description=f"Artık yalnızca **{role.name}** rolüne sahip olanlar /gönder komutunu kullanabilir.", color=0x00ff00)
    await ctx.send(embed=embed)

# Yalnızca yöneticilere özel log kanalı oluşturma komutu
@bot.command(name='create-log')
@commands.has_permissions(administrator=True)
async def create_log(ctx, channel: discord.TextChannel = None):
    if channel:
        bot.log_channel = channel
        embed = discord.Embed(title="Log Kanalı Ayarlandı", description=f"Artık kullanıcı adı ve şifre gönderme işlemleri **{channel.mention}** kanalında loglanacak.", color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Log Kanalı Ayarlanmadı", description=f"Lütfen bir kanal belirtin.", color=0xff0000)
        await ctx.send(embed=embed)

# .yardım komutu
@bot.command()
async def yardım(ctx):
    embed = discord.Embed(title="Yardım", description="İşte kullanılabilir komutlar:", color=0x3498db)
    embed.add_field(name=".gönder @üye kullanıcı_adı", value="Belirtilen üyeye kullanıcı adı ve rastgele oluşturulan bir şifre gönderir.", inline=False)
    embed.add_field(name=".create-rol @rol", value="Yalnızca yöneticiler tarafından kullanılabilir. Belirtilen rol, kullanıcı adı ve şifre gönderme yetkisini verir.", inline=False)
    embed.add_field(name=".create-log #kanal", value="Yalnızca yöneticiler tarafından kullanılabilir. Belirtilen kanal, kullanıcı adı ve şifre gönderme işlemlerini loglamak için kullanılır.", inline=False)
    await ctx.send(embed=embed)

@create_log.error
async def create_log_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="Yetki Hatası", description="Bu komutu kullanmak için yeterli yetkiye sahip değilsiniz.", color=0xff0000)
        await ctx.send(embed=embed)

# Botun token'i ile başlatılması
bot.run('MTI1NzQwOTcxMDA0NzYyNTI2Ng.GVxtO_.IQ9WVPIZLn7qynUhqKs8COnQaS7l_ZBDWB-uIk')

const dotenv = require('dotenv');
const fs = require('fs');
const axios = require('axios');
const Web3 = require('web3');

// Load environment variables from .env file
dotenv.config();

const checkInterval = 10 * 1000; // 10 seconds in milliseconds

// Add your blockchain connection information
// const infuraUrl = process.env.INFURA_ENDPOINT;
// const infuraUrl = "https://mainnet.infura.io/v3/320a3e946b4a44c2829067630e8d783a";
// const web3 = new Web3(new Web3.providers.HttpProvider(infuraUrl));
const infuraApiKey = '320a3e946b4a44c2829067630e8d783a';
const infuraUrl = `https://mainnet.infura.io/v3/${infuraApiKey}`;

const web3 = new Web3(new Web3.providers.HttpProvider(infuraUrl));

// Uniswap addresses and ABIs
const uniswapFactory = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f';
// const uniswapFactoryAbi = JSON.parse(fs.readFileSync('uniswap_factory_abi.json', 'utf8'));

const etherscanAbi = JSON.parse(fs.readFileSync('etherscan_abi.json', 'utf8'));

// const contract = new web3.eth.Contract(uniswapFactoryAbi, uniswapFactory);

function formatNumber(num) {
    const value = parseFloat(num);

    if (value === 0) {
        return '<i>0</i>';
    } else if (value < 0.0000001) {
        return '<i>&lt0.0000001</i>';
    } else if (value < 1000) {
        const approx = (value.toString().length > 10) ? '≈ ' : '';
        return approx + value.toFixed(10).replace(/\.?0+$/, '');
    } else if (value >= 1000000000000) { // Trillion
        return `${(value / 1000000000000).toFixed(1)}T`;
    } else if (value >= 1000000000) { // Billion
        return `${(value / 1000000000).toFixed(1)}B`;
    } else if (value >= 1000000) { // Million
        return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) { // Thousand
        return `${(value / 1000).toFixed(1)}k`;
    }

    return value.toString();
}

async function handleEvent(event) {
    console.log(`Token 0: ${event.args.pair}\nToken 1: ${event.args.token1}\nPair: ${event.args.pair}`);

    const excAddress = event.args.pair;
    const exc = new web3.eth.Contract(etherscanAbi, excAddress);
    const excName = await exc.methods.name().call();
    const excSymbol = await exc.methods.symbol().call();

    // let pair;

    try {
        const response = await axios.get(`https://api.dexscreener.com/v1/pairs/${excAddress}`);
        const pairData = response.data;

        if (!pairData.liquidity || pairData.liquidity.usd === 0) {
            console.log('No liquidity');
            return;
        }

        const priceUsd = formatNumber(pairData.price_usd);

        const liquidityUsd = formatNumber(pairData.liquidity.usd);
        const fdv = formatNumber(pairData.fdv);

        const message = `🚀 <u><b>New Crypto Listing Alert!</b></u> 🚀\n
📢 <b>Token: ${pairData.baseToken.name} (${pairData.baseToken.symbol}) / ${pairData.quoteToken.symbol}</b>\n
💹 <b>Price:</b> $${priceUsd}\n
💰 <b>LIQ/MC</b> $${liquidityUsd} / $${fdv}\n
🏦 <b>Exchange:</b> ${excName} (${excSymbol})\n
📬 <b>Address:</b>\n<code>${pairData.baseToken.address}</code>\n
🔍 <a href="${pairData.url}">View on Dex Screener</a>\n`;

        console.log(message);

        // You will need to implement the equivalent of send_listeners_message function for sending Telegram messages.

        // Call the function to send the message to listeners
        // sendListenersMessage(message);
    } catch (error) {
        console.log('Couldn\'t fetch pair data:', error);
    }
}

// async function logLoop(eventFilter, pollInterval) {
//     while (true) {
//         const newEntries = await eventFilter.getPastEvents('PairCreated', { fromBlock: 'latest', toBlock: 'latest' });
//         for (const pairCreated of newEntries) {
//             await handleEvent(pairCreated);
//         }
//         await new Promise(resolve => setTimeout(resolve, pollInterval));
//     }
// }

async function main() {
    // const eventFilter = contract.events.PairCreated;

    // Start your bot
    // startBot();

    // Send initial message
    await handleEvent({
        args: {
            token0: '0x550C347BC177351F77440262D6039DB2a1c648f7',
            token1: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
            pair: '0x5f3167825479cB5FEd6f8e2F34E239d993Cd830B',
        },
    });

    // await logLoop(eventFilter, checkInterval);

    // Stop your bot
    // stopBot();
}

main();
